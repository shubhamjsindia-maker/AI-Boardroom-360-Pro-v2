"""Controlled Excel import: explicit period columns, standard account keys and no silent defaults."""
from io import BytesIO
from .financial import LABELS, validate_dataset

TEMPLATE_ROWS=['revenue','other_income','materials','employee_expense','other_expense','ebitda','depreciation','finance_cost','pbt','tax','pat','oci','total_comprehensive_income','ppe','inventory','receivables','cash','other_assets','total_assets','equity','borrowings','payables','other_liabilities','total_equity_liabilities','opening_cash','cash_operations','cash_investing','cash_financing','closing_cash','opening_equity','equity_transactions','closing_equity']

def read_workbook(file_bytes):
    from openpyxl import load_workbook
    wb=load_workbook(BytesIO(file_bytes),read_only=True,data_only=True)
    if 'Company_Master' not in wb.sheetnames or 'Financial_Data' not in wb.sheetnames:
        raise ValueError('Workbook must contain Company_Master and Financial_Data worksheets. Download the Phase 1 template.')
    meta={str(row[0]):row[1] for row in wb['Company_Master'].iter_rows(min_row=2,values_only=True) if row[0]}
    ws=wb['Financial_Data']; rows=list(ws.iter_rows(values_only=True))
    if not rows or len(rows[0])<3 or str(rows[0][0]).strip()!='account_key':
        raise ValueError('Financial_Data header must start with account_key and include two to five year columns.')
    years=[str(y).strip() for y in rows[0][2:] if y is not None]
    if len(years)!=len(set(years)) or not 2<=len(years)<=5:
        raise ValueError('Provide 2–5 unique historical financial years.')
    records={y:{} for y in years}; seen=set()
    for row in rows[1:]:
        key=row[0]
        if key is None:continue
        key=str(key).strip()
        if key in seen:raise ValueError(f'Duplicate account_key: {key}')
        seen.add(key)
        if key not in TEMPLATE_ROWS:raise ValueError(f'Unknown account_key: {key}')
        for index,y in enumerate(years): records[y][key]=row[index+2] if index+2<len(row) else None
    data={'company':str(meta.get('Company Name','Imported Company')),'basis':str(meta.get('Reporting Basis','Standalone')),'unit':'INR lakh','source':'User-uploaded Excel; not independently audited','periods':records}
    return data,validate_dataset(data)

def make_template(data=None):
    """Build formatted template with explicit account keys; figures remain editable."""
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill,Alignment
    from openpyxl.utils import get_column_letter
    wb=Workbook(); master=wb.active;master.title='Company_Master'
    master.append(['Field','Value'])
    for item,value in [('Company Name',(data or {}).get('company','Your Company Pvt. Ltd.')),('Reporting Basis',(data or {}).get('basis','Standalone')),('Accounting Framework','Schedule III Division II — Ind AS'),('Internal Unit','INR lakh'),('Source Status','Unverified until reviewed')]:master.append([item,value])
    ws=wb.create_sheet('Financial_Data')
    years=list((data or {}).get('periods',{'FY2024':{},'FY2025':{}}))
    ws.append(['account_key','Financial Statement Line Item']+years)
    for key in TEMPLATE_ROWS:
        values=[(data or {}).get('periods',{}).get(y,{}).get(key,None) for y in years]
        ws.append([key,LABELS.get(key,key)]+values)
    notes=wb.create_sheet('Instructions')
    for row in [ ['AI Boardroom 360 Pro | Phase 1 Excel Template'],['Enter financial amounts in INR lakh; do not alter account_key cells.'],['Do not leave required amounts blank; explicitly enter zero only if truly zero.'],['Data must represent the same reporting basis and currency for every period.'],['The current Phase 1 template is a normalized statement import, not yet a full Schedule III notes template.'],['Published historical figures require professional verification and source references.']]:notes.append(row)
    for sh in wb:
        sh.freeze_panes='C2' if sh.title=='Financial_Data' else 'A2'
        sh.column_dimensions['A'].width=38
        sh.column_dimensions['B'].width=48
        for index in range(3,9):sh.column_dimensions[get_column_letter(index)].width=18
        for c in sh[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='16324F');c.alignment=Alignment(wrap_text=True)
    output=BytesIO();wb.save(output);return output.getvalue()
