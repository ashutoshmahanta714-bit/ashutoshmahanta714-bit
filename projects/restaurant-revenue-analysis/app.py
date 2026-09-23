from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Restaurant Revenue | Analyst Portfolio", layout="wide")
DATA = Path(__file__).parent / "data" / "tips.csv"
df = pd.read_csv(DATA)
df["tip_rate"] = df["tip"] / df["total_bill"]
st.title("Restaurant revenue and tipping")
st.caption("Public seaborn tips sample · 244 bills · USD · illustrative analysis, not a live business")
days = st.multiselect("Day", ["Thur", "Fri", "Sat", "Sun"], default=["Thur", "Fri", "Sat", "Sun"])
meals = st.multiselect("Meal", ["Lunch", "Dinner"], default=["Lunch", "Dinner"])
f = df[df.day.isin(days) & df.time.isin(meals)]
if f.empty:
    st.info("Select at least one day and meal with matching records.")
    st.stop()
a,b,c,d = st.columns(4)
a.metric("Bills", f"{len(f):,}")
b.metric("Revenue", f"${f.total_bill.sum():,.2f}")
c.metric("Average bill", f"${f.total_bill.mean():,.2f}")
d.metric("Weighted tip rate", f"{100*f.tip.sum()/f.total_bill.sum():.1f}%")
by_day = f.groupby("day", as_index=False).agg(bills=("total_bill","size"), revenue=("total_bill","sum"), tips=("tip","sum"))
by_day["day"] = pd.Categorical(by_day.day, ["Thur","Fri","Sat","Sun"], ordered=True)
by_day = by_day.sort_values("day")
left,right = st.columns(2)
left.plotly_chart(px.bar(by_day, x="day", y="revenue", text_auto=".2f", title="Revenue by day"), use_container_width=True)
right.plotly_chart(px.scatter(f, x="total_bill", y="tip", color="time", hover_data=["day","size"], title="Bill and tip by meal"), use_container_width=True)
st.subheader("Segment detail")
st.dataframe(f.groupby(["day","time"], as_index=False).agg(bills=("total_bill","size"), average_bill=("total_bill","mean"), revenue=("total_bill","sum")).round(2), hide_index=True, use_container_width=True)
st.caption("Observed associations only. The sample has no calendar date, staffing, costs or location; it cannot support growth, profit or causal claims.")
