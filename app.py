"""AI Boardroom 360 Pro — Phase 1 working alpha. Historical data only."""
import json
from io import BytesIO
import pandas as pd
import streamlit as st
from core.demo import sample_company
from core.financial import STATEMENTS, LABELS, normalize, validate_dataset, ratios
from core.importer import read_workbook, make_template
from core.reporting import excel_report, pdf_report

st.set_page_config(page_title='AI Boardroom 360 Pro',page_icon='📊',layout='wide')
st.markdown('''<style>.block-container{padding-top:1.7rem}.stMetric{background:#f2f6fb;border:1px solid #dbe4f0;border-radius:11px;padding:13px}.stTabs [data-baseweb="tab-list"]{gap:12px}</style>''',unsafe_allow_html=True)

if 'data' not in st.session_state: st.session_state.data=sample_company()
if 'version' not in st.session_state: st.session_state.version=1
if 'source_approved' not in st.session_state: st.session_state.source_approved=False

def currency(value):
    if value is None:return 'Not available'
    return f'₹{float(value):,.2f} L'

def table_for(items,data):
    years=list(data['periods']);records=[]
    for key,label in items:
        row={'Financial Line Item':label}
        for year in years:
            row[year]=float(data['periods'][year][key]) if data['periods'][year].get(key) not in ('',None) else None
        records.append(row)
    return pd.DataFrame(records).set_index('Financial Line Item')

data=st.session_state.data
findings=validate_dataset(data)
with st.sidebar:
    st.title('AI Boardroom 360 Pro')
    st.caption('Phase 1 · Historical Financial Intelligence')
    mode=st.radio('Workspace',['Guided CA Workflow','Professional Analyst'],label_visibility='visible')
    st.divider()
    page=st.radio('Navigation',['Executive Overview','Company Master','Data Studio','Financial Statements','Financial Ratios','Validation Centre','Review & Export'])
    st.divider()
    st.caption('Demo-only: in-memory session data. No permanent user accounts or approval storage.')
    st.caption('Existing AI Boardroom 1.x is unaffected.')

st.title(page)
st.caption(f"{data['company']}  ·  {data.get('basis','Standalone')}  ·  INR lakh  ·  {'READY FOR REVIEW' if not findings else 'VALIDATION REQUIRED'}")
if mode=='Guided CA Workflow':
    st.info('Guided mode: 1. Company Setup → 2. Import → 3. View Financials → 4. Validate → 5. Review & Export')

if page=='Executive Overview':
    year=list(data['periods'])[-1];p=data['periods'][year];r=ratios(p)
    c=st.columns(4)
    for col,(lab,val) in zip(c,[('Revenue',currency(p.get('revenue'))),('EBITDA',currency(p.get('ebitda'))),('Profit After Tax',currency(p.get('pat'))),('Closing Cash',currency(p.get('cash')))]):col.metric(lab,val)
    c=st.columns(4)
    for col,lab in zip(c,['EBITDA Margin (%)','Net Profit Margin (%)','Interest Coverage (x)','Net Borrowings / EBITDA (x)']):
        val=r.get(lab);col.metric(lab,'N/A' if val is None else f'{float(val):.2f}'+('%' if '(%)' in lab else 'x'))
    st.subheader('Historical Trends')
    df=pd.DataFrame([{'Financial year':y,'Revenue':float(v.get('revenue',0)),'EBITDA':float(v.get('ebitda',0)),'Profit After Tax':float(v.get('pat',0))} for y,v in data['periods'].items()]).set_index('Financial year')
    st.line_chart(df)
    st.caption('Financial metrics are derived from currently loaded figures. Figures from a user import are not independently verified.')
elif page=='Company Master':
    st.subheader('Reporting Profile')
    st.text_input('Company / Entity',value=data['company'],disabled=True)
    st.text_input('Reporting basis',value=data.get('basis','Standalone'),disabled=True)
    st.text_input('Internal reporting unit',value=data.get('unit','INR lakh'),disabled=True)
    st.write('Historical periods:',', '.join(data['periods']))
    st.caption('Phase 1 alpha: Company setup is loaded from the workbook rather than edited in the browser.')
elif page=='Data Studio':
    st.subheader('Import Historical Financial Data')
    st.write('The initial alpha accepts a normalized Excel template. Uploads replace session data only; they are not stored permanently.')
    st.download_button('Download blank Excel template',data=make_template(),file_name='AI_Boardroom_Phase1_Blank_Template.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.download_button('Download complete Nova sample workbook',data=make_template(sample_company()),file_name='Nova_Manufacturing_Five_Year_Sample.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    upload=st.file_uploader('Upload Phase 1 workbook',type=['xlsx'])
    if upload is not None:
        try:
            incoming,new_findings=read_workbook(upload.getvalue())
            st.success('Excel workbook structure recognized.')
            st.write('Company:',incoming['company'],'| Periods:',', '.join(incoming['periods']))
            if new_findings:
                st.error(f'{len(new_findings)} validation issue(s) found. Import blocked until corrected.')
                st.dataframe(pd.DataFrame(new_findings),hide_index=True,use_container_width=True)
            else:
                st.success('Required statement reconciliations passed.')
                if st.button('Use validated upload',type='primary'):
                    st.session_state.data=incoming;st.session_state.source_approved=False;st.session_state.version+=1;st.rerun()
        except Exception as exc:st.error(f'Unable to read this workbook: {exc}')
    st.divider();st.subheader('PDF extraction status')
    st.warning('Annual-report PDF extraction and source-page verification are NOT implemented in this alpha. Do not interpret the Excel importer as a complete Schedule III / PDF workflow.')
elif page=='Financial Statements':
    for tab,(name,items) in zip(st.tabs(list(STATEMENTS)),STATEMENTS.items()):
        with tab:
            st.subheader(name)
            st.dataframe(table_for(items,data),use_container_width=True)
            st.caption('Simplified normalized statements; complete Schedule III note disclosures remain a Phase 1 development work package.')
elif page=='Financial Ratios':
    years=list(data['periods']);names=list(ratios(data['periods'][years[-1]]))
    df=pd.DataFrame([{'Metric':name,**{y:(float(ratios(data['periods'][y]).get(name)) if ratios(data['periods'][y]).get(name) is not None else None) for y in years}} for name in names]).set_index('Metric')
    st.dataframe(df,use_container_width=True)
    st.caption('Current ratio is simplified because the alpha does not yet separate all current/non-current asset and liability categories.')
elif page=='Validation Centre':
    st.subheader('Financial Reconciliation Checks')
    if not findings:st.success(f'All 11 core arithmetic and cross-statement checks passed for {len(data["periods"])} years.')
    else:st.error(f'{len(findings)} issues require correction.');st.dataframe(pd.DataFrame(findings),hide_index=True,use_container_width=True)
    st.caption('Passing arithmetic checks does not establish audit assurance, source authenticity or full Schedule III compliance.')
elif page=='Review & Export':
    st.subheader('Financial Review & Export')
    st.write('Current session dataset version:',st.session_state.version)
    st.write('Source status:',data.get('source','Unspecified'))
    if findings:st.error('Critical validation issues prevent generating a clean reconciliation package.')
    else:
        st.success('Core financial checks passed — eligible for DRAFT export.')
        st.download_button('Download historical financial workbook',data=excel_report(data),file_name='AI_Boardroom_Historical_Financials_DRAFT.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.download_button('Download historical PDF summary',data=pdf_report(data,findings),file_name='AI_Boardroom_Historical_Review_DRAFT.pdf',mime='application/pdf')
    st.warning('Maker-checker approvals and immutable database snapshots are NOT implemented. Exports are DRAFT / UNVERIFIED and not audited financial statements.')
