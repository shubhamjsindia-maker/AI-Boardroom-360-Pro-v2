"""Entirely fictional, arithmetically reconciled reference data."""

def sample_company():
    periods={};opening_cash=70;opening_equity=320
    for i,year in enumerate(range(2022,2027)):
        revenue=800+120*i;other_income=10+2*i;materials=440+60*i;employees=115+15*i;other_expense=125+13*i
        ebitda=revenue+other_income-materials-employees-other_expense
        depreciation=25+3*i;interest=20+2*i;pbt=ebitda-depreciation-interest;tax=round(pbt*0.25,2);pat=pbt-tax;oci=2+i
        closing_cash=opening_cash+25+10*i
        cash_operations=90+15*i;cash_investing=-(65+6*i);cash_financing=closing_cash-opening_cash-cash_operations-cash_investing
        equity_transactions=-20
        equity=opening_equity+pat+oci+equity_transactions
        ppe=500+55*i;inventory=120+15*i;receivables=140+19*i;other_assets=50+7*i
        assets=ppe+inventory+receivables+closing_cash+other_assets
        borrowings=300+20*i;payables=110+12*i
        other_liabilities=round(assets-equity-borrowings-payables,2)
        rec={'revenue':revenue,'other_income':other_income,'materials':materials,'employee_expense':employees,'other_expense':other_expense,'ebitda':ebitda,'depreciation':depreciation,'finance_cost':interest,'pbt':pbt,'tax':tax,'pat':pat,'oci':oci,'total_comprehensive_income':pat+oci,'ppe':ppe,'inventory':inventory,'receivables':receivables,'cash':closing_cash,'other_assets':other_assets,'total_assets':assets,'equity':equity,'borrowings':borrowings,'payables':payables,'other_liabilities':other_liabilities,'total_equity_liabilities':assets,'opening_cash':opening_cash,'cash_operations':cash_operations,'cash_investing':cash_investing,'cash_financing':cash_financing,'closing_cash':closing_cash,'opening_equity':opening_equity,'equity_transactions':equity_transactions,'closing_equity':equity}
        periods[f'FY{year}']={k:str(v) for k,v in rec.items()}
        opening_cash=closing_cash;opening_equity=equity
    return {'company':'Nova Manufacturing Pvt. Ltd. (Fictional)','basis':'Standalone','unit':'INR lakh','source':'Synthetic demonstration figures; NOT sourced from an actual annual report','periods':periods}
