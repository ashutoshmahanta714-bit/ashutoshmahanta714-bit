# Tableau calculated fields

Connect Tableau Desktop/Public to `../data/tips.csv`. Confirm Total Bill and Tip are numbers, Size is a whole number. Rename fields if desired.

Create these calculated fields exactly:

**Bills**
```tableau
COUNT([total_bill])
```

**Revenue**
```tableau
SUM([total_bill])
```

**Tips Collected**
```tableau
SUM([tip])
```

**Average Bill**
```tableau
SUM([total_bill]) / COUNT([total_bill])
```

**Weighted Tip Rate**
```tableau
SUM([tip]) / SUM([total_bill])
```

**Day Order**
```tableau
CASE [day] WHEN "Thur" THEN 1 WHEN "Fri" THEN 2 WHEN "Sat" THEN 3 ELSE 4 END
```

Format currency measures as USD and Weighted Tip Rate as percentage. Sort Day by Day Order ascending. Never average row-level tip percentages when reporting the aggregate weighted rate.
