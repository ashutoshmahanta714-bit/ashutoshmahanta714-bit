# Tableau dashboard build

This is a **build kit**, not a finished TWBX file.

1. Connect to `../data/tips.csv` as a text file. Verify 244 rows and types. Add the fields in `Calculated-Fields.md`.
2. Create **KPI** worksheet using Measure Names/Values for Bills, Revenue, Average Bill, and Weighted Tip Rate.
3. Create **Revenue by Day**: Day on Columns, Revenue on Rows, bars with labels, sorted Thur → Fri → Sat → Sun.
4. Create **Bill vs Tip**: total_bill on Columns, tip on Rows, circle marks, time on Color, day and size on Tooltip. Turn off aggregation of measures for a mark per row.
5. Create **Segment Table**: day and time on Rows; Bills, Revenue, Average Bill, Weighted Tip Rate on Text.
6. Create a dashboard, size 1200 × 800. Put title and scope at top, KPI row, two charts side by side, segment table beneath. Add Day and Time filters and apply them to all relevant sheets.
7. Validate 244 bills, $4,827.77 total bills and $731.58 tips with filters cleared. Save as a packaged workbook in Tableau Desktop/Public and inspect it there before sharing.

The dataset has no calendar dates, costs, locations or staff identifiers. Do not infer growth, margin, staffing effects or causality. If using Tableau Public, remember published workbook data is public.
