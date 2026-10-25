"""Deterministic historical financial validation and ratios. Monetary values in INR lakh."""
from decimal import Decimal, InvalidOperation
from typing import Mapping

STATEMENTS = {
    'Profit & Loss': [('revenue','Revenue from Operations'), ('other_income','Other Income'), ('materials','Cost of Materials and Other Direct Costs'), ('employee_expense','Employee Benefits Expense'), ('other_expense','Other Operating Expenses'), ('ebitda','EBITDA — Analytical Measure'), ('depreciation','Depreciation and Amortisation'), ('finance_cost','Finance Costs'), ('pbt','Profit Before Tax'), ('tax','Tax Expense'), ('pat','Profit for the Year'), ('oci','Other Comprehensive Income'), ('total_comprehensive_income','Total Comprehensive Income')],
    'Balance Sheet': [('ppe','Property, Plant and Equipment'), ('inventory','Inventories'), ('receivables','Trade Receivables'), ('cash','Cash and Cash Equivalents'), ('other_assets','Other Assets'), ('total_assets','Total Assets'), ('equity','Total Equity'), ('borrowings','Borrowings'), ('payables','Trade Payables'), ('other_liabilities','Other Liabilities'), ('total_equity_liabilities','Total Equity and Liabilities')],
    'Cash Flow': [('opening_cash','Opening Cash and Cash Equivalents'), ('cash_operations','Net Cash from Operating Activities'), ('cash_investing','Net Cash from Investing Activities'), ('cash_financing','Net Cash from Financing Activities'), ('closing_cash','Closing Cash and Cash Equivalents')],
    'Changes in Equity': [('opening_equity','Opening Total Equity'), ('pat','Profit for the Year'), ('oci','Other Comprehensive Income'), ('equity_transactions','Net Owner Transactions and Other Equity Movements'), ('closing_equity','Closing Total Equity')]
}
LABELS = {key: label for entries in STATEMENTS.values() for key,label in entries}
REQUIRED = sorted(set(LABELS) | {'opening_cash','opening_equity','equity_transactions'})


def decimal(value):
    if value is None or value == '':
        raise ValueError('Missing financial value (must not be treated as zero)')
    try:
        result = Decimal(str(value).replace(',', ''))
    except (InvalidOperation, ValueError):
        raise ValueError(f'Invalid financial amount: {value!r}')
    if not result.is_finite():
        raise ValueError('Financial amount must be finite')
    return result


def normalize(raw: Mapping):
    """Reject missing items; preserve source-provided values; no balancing plugs."""
    errors=[]; out={}
    for key in REQUIRED:
        try: out[key]=decimal(raw.get(key))
        except ValueError as exc: errors.append(f'{LABELS.get(key,key)}: {exc}')
    return out,errors


def validate(period):
    x,errors=normalize(period)
    if errors: return [{'rule':'DATA','severity':'Critical','message':v,'difference':None} for v in errors]
    tests = [
        ('PL-01', x['ebitda'], x['revenue']+x['other_income']-x['materials']-x['employee_expense']-x['other_expense'], 'EBITDA does not reconcile with operating inputs'),
        ('PL-02',x['pbt'],x['ebitda']-x['depreciation']-x['finance_cost'],'Profit before tax does not reconcile'),
        ('PL-03',x['pat'],x['pbt']-x['tax'],'Profit for the year does not reconcile'),
        ('PL-04',x['total_comprehensive_income'],x['pat']+x['oci'],'Total comprehensive income does not reconcile'),
        ('BS-01',x['total_assets'],sum((x[k] for k in ('ppe','inventory','receivables','cash','other_assets')),Decimal('0')),'Asset line items do not sum to total assets'),
        ('BS-02',x['total_equity_liabilities'],sum((x[k] for k in ('equity','borrowings','payables','other_liabilities')),Decimal('0')),'Equity and liabilities do not sum to total'),
        ('BS-03',x['total_assets'],x['total_equity_liabilities'],'Balance Sheet does not balance'),
        ('CF-01',x['closing_cash'],x['opening_cash']+x['cash_operations']+x['cash_investing']+x['cash_financing'],'Cash flow movements do not reconcile'),
        ('CF-02',x['closing_cash'],x['cash'],'Cash Flow closing balance disagrees with Balance Sheet cash'),
        ('EQ-01',x['closing_equity'],x['opening_equity']+x['pat']+x['oci']+x['equity_transactions'],'Equity statement does not reconcile'),
        ('EQ-02',x['closing_equity'],x['equity'],'Statement of Changes in Equity disagrees with Balance Sheet')
    ]
    findings=[]
    for rule,reported,expected,message in tests:
        diff=reported-expected
        if abs(diff)>Decimal('0.01'):
            findings.append({'rule':rule,'severity':'Critical','message':message,'difference':str(diff)})
    return findings


def ratio(num,den):
    return None if den is None or den==0 else num/den


def ratios(period):
    x,errors=normalize(period)
    if errors: return {}
    current_assets=x['inventory']+x['receivables']+x['cash']
    current_liabilities=x['payables']+x['other_liabilities']
    return {
        'EBITDA Margin (%)': ratio(x['ebitda']*100,x['revenue']),
        'Net Profit Margin (%)':ratio(x['pat']*100,x['revenue']),
        'Interest Coverage (x)':ratio(x['ebitda']-x['depreciation'],x['finance_cost']),
        'Borrowings / Equity (x)':ratio(x['borrowings'],x['equity']),
        'Net Borrowings / EBITDA (x)':ratio(x['borrowings']-x['cash'],x['ebitda']),
        'Current Ratio (x) — simplified':ratio(current_assets,current_liabilities),
        'Operating Cash Conversion (%)':ratio(x['cash_operations']*100,x['ebitda']),
    }


def validate_dataset(data):
    years=data.get('periods',{})
    findings=[]
    if not 2 <= len(years) <= 5:
        findings.append({'period':'Dataset','rule':'PERIOD-01','severity':'Critical','message':'Select between two and five historical years','difference':None})
    for year,record in sorted(years.items()):
        findings += [{'period':year,**item} for item in validate(record)]
    return findings
