from pathlib import Path
import json
import pandas as pd
import streamlit as st
from model import load_data, train, predict, NUMERIC, CATEGORIES, FEATURES

st.set_page_config(page_title='StockSense | Inventory Risk', page_icon='📦', layout='wide')
st.title('StockSense')
st.caption('Inventory risk analysis · Ashutosh Mahanta')
st.info('Learning prototype: classifies stockout versus overstock in the supplied dataset. '
        'It does not forecast future stockouts or identify a healthy-stock class.')

@st.cache_resource
def trained():
    return train()

@st.cache_data
def dataset():
    return load_data()

with st.spinner('Preparing the inventory model…'):
    model, report = trained()
data = dataset()
page = st.sidebar.radio('Workspace', ['Overview', 'Single product', 'Batch predictions', 'Model evaluation'])
st.sidebar.caption('Built from the existing Google Colab workflow. No account or API key required.')

if page == 'Overview':
    a,b,c = st.columns(3)
    a.metric('Dataset records', f'{len(data):,}')
    b.metric('Stockout-labelled records', f'{(data.stock_status=="stockout").sum():,}')
    c.metric('Input features', len(FEATURES))
    st.subheader('Inventory dataset')
    season = st.selectbox('Season', ['All'] + CATEGORIES['season'])
    subset = data if season == 'All' else data[data.season == season]
    st.bar_chart(subset.stock_status.value_counts())
    st.dataframe(subset, hide_index=True, use_container_width=True)
    st.download_button('Download sample upload template', data[FEATURES].head(10).to_csv(index=False),
                       'inventory_template.csv', 'text/csv')
    st.warning('All 5,000 labels follow current_stock < reorder_point → stockout; '
               'current_stock > reorder_point → overstock. Above the reorder point does not '
               'necessarily mean excess stock in real operations. Dataset origin is unverified.')
elif page == 'Single product':
    st.subheader('Assess one product')
    with st.form('product'):
        values = {}
        columns = st.columns(2)
        for i, field in enumerate(NUMERIC):
            with columns[i % 2]:
                kwargs = {} if field == 'forecast_error' else {'min_value':0.0}
                values[field] = st.number_input(field.replace('_',' ').capitalize(),
                                                value=float(data[field].median()), **kwargs)
        for i, (field, choices) in enumerate(CATEGORIES.items()):
            with columns[i % 2]:
                values[field] = st.selectbox(field.replace('_',' ').capitalize(), choices)
        submitted = st.form_submit_button('Assess inventory', type='primary')
    if submitted:
        try:
            out = predict(model,pd.DataFrame([values]))
            row = out.iloc[0]
            a,b,c = st.columns(3)
            a.metric('Model classification',row.model_prediction.title())
            b.metric('Direct stock rule',row.stock_rule.title())
            c.metric('Units vs reorder point',f'{row.units_vs_reorder_point:,.2f}')
            st.caption(f'Model stockout probability: {row.model_stockout_probability:.1%}. '
                       'This class-weighted model score is not calibrated operational risk.')
            if row.stock_rule == 'at reorder point':
                st.warning('At the reorder point: this boundary is absent from the training data. Review manually.')
            elif row.model_prediction != row.stock_rule:
                st.warning('Model and dataset rule disagree. Review inputs and use the explicit rule as a benchmark.')
            st.write('Review replenishment timing and supplier lead time.' if row.stock_rule=='stockout'
                     else 'Review demand and holding costs before changing order quantities.')
            st.dataframe(out, hide_index=True)
        except ValueError as e:
            st.error(str(e))
elif page == 'Batch predictions':
    st.subheader('Upload inventory records')
    st.write('Upload CSV or Excel with the 10 input columns. Extra columns are ignored; no stock_status label is required.')
    st.download_button('Download CSV template',data[FEATURES].head(10).to_csv(index=False),
                       'inventory_template.csv','text/csv')
    file = st.file_uploader('Inventory file (up to 10 MB, 10,000 rows)',type=['csv','xlsx'])
    if file:
        if file.size > 10*1024*1024:
            st.error('File exceeds 10 MB.')
        else:
            try:
                frame = pd.read_csv(file) if file.name.lower().endswith('.csv') else pd.read_excel(file)
                out = predict(model,frame)
                st.success(f'Assessed {len(out):,} products.')
                st.dataframe(out,hide_index=True,use_container_width=True)
                st.download_button('Download predictions',out.to_csv(index=False),
                                   'inventory_predictions.csv','text/csv')
            except Exception as e:
                st.error(f'Could not assess this file: {e}')
    st.caption('Uploaded rows are processed in memory for this session and are not written to disk by this app.')
else:
    st.subheader('Evaluation and limitations')
    st.write('80/20 stratified split, random_state=100. Logistic Regression tuning uses five-fold '
             'cross-validation on training data only. Encoding and scaling live inside the pipeline.')
    rows = []
    for name,key in [('Logistic Regression','heldout_test'),('Direct stock rule','direct_rule'),('Majority baseline','majority_baseline')]:
        rows.append({'Model':name,**{k:v for k,v in report[key].items() if k!='confusion_matrix'}})
    st.dataframe(pd.DataFrame(rows).set_index('Model').style.format('{:.2%}'))
    st.write('Confusion matrix: rows = actual, columns = predicted.')
    st.dataframe(pd.DataFrame(report['heldout_test']['confusion_matrix'],
                             index=['Actual overstock','Actual stockout'],
                             columns=['Predicted overstock','Predicted stockout']))
    st.warning('High scores mostly measure recovery of the existing label rule. '
               'There are no product IDs, timestamps, healthy-stock labels, cost targets, or independently '
               'observed future outcomes. Operational forecasting and cost savings have not been validated.')
    st.json(report)
    st.download_button('Download evaluation report',json.dumps(report,indent=2),'evaluation.json','application/json')
