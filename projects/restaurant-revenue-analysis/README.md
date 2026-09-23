# Restaurant Revenue & Tipping Analysis

An entry-level data analyst case study using the public [seaborn tips dataset](https://github.com/mwaskom/seaborn-data/blob/master/tips.csv). It combines SQL aggregation with an interactive Streamlit dashboard, plus [Power BI](power-bi/README.md) and [Tableau](tableau/README.md) build kits with native formulas and report layouts. These kits are not completed PBIX or TWBX files. The 244 records are a sample of restaurant bills, not sales from YASH Technologies or an operating business.

## Business questions
- Which observed days contribute most revenue and bills?
- How do bill sizes and weighted tip rates differ by segment?
- Which party sizes have enough records for a useful comparison?

## Verified snapshot
- 244 bills, **$4,827.77** total bill value, **$731.58** total tips.
- Saturday: 87 bills and **$1,778.40** bill value; Sunday: 76 bills and **$1,627.16**.
- These totals describe this sample only. Friday has 19 records, so comparisons require care.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
Run `analysis.sql` after importing `data/tips.csv` into a SQLite table named `tips`. Columns are `total_bill, tip, sex, smoker, day, time, size`. Revenue means sum of total bills; weighted tip rate means sum(tip)/sum(total_bill). Filters change all dashboard visuals.

## Data quality and limits
No missing values in the supplied 244 records. Bill and tip values are positive. The data lack dates, costs, locations, order IDs, and staff. There is no basis for trend, profitability, experiment, or causal claims. The sample is public and its currency is USD. A Power BI report has **not** been created for this project.

## Next extension
Connect a dated transaction table and cost data; model fact bills and day/meal dimensions in Power BI; add period comparisons and margin measures only after those fields exist.
