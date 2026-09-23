# Power BI dashboard build

This is a **build kit**, not a finished PBIX file. Open Power BI Desktop and create a report from the supplied source and measures.

1. Home → Get data → Blank query → Advanced Editor. Paste `PowerQuery-Tips.m` and name the loaded table **Tips**. Alternatively, import `../data/tips.csv` and apply the same types and renamed columns.
2. In Model view create each measure in `Measures.dax` separately. Set Day to sort by Day Sort.
3. Use a 16:9 report page. Add a title, dataset subtitle, four cards (Bills, Revenue, Average Bill, Weighted Tip Rate), a clustered column chart (Day / Revenue), a scatterplot (Total Bill / Tip, Meal as legend), and a matrix (Day, Meal / Bills, Revenue, Average Bill, Weighted Tip Rate).
4. Add Day and Meal slicers; check that all visuals cross-filter. Add a footer: “Public sample; no dates, costs or locations. Descriptive analysis only.”
5. With all days and meals selected, validate 244 bills, $4,827.77 revenue, and $731.58 tips. Weighted tip rate should be about 15.15%.
6. Save as `Restaurant_Revenue_Analysis.pbix`. Publish only if your data privacy and Power BI account settings permit it.

The source is the public seaborn tips CSV. Revenue is bill value, not profit. There is no date field, so avoid monthly trends and year-over-year calculations. The sex and smoker columns are loaded for source fidelity but are intentionally omitted from the report: those attributes should not be treated as causal drivers.
