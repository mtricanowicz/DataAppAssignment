import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## My additions:")
#st.write("### (1) add a drop down for Category (https://docs.streamlit.io/library/api-reference/widgets/st.selectbox)")
#st.write("### (2) add a multi-select for Sub_Category *in the selected Category (1)* (https://docs.streamlit.io/library/api-reference/widgets/st.multiselect)")
#st.write("### (3) show a line chart of sales for the selected items in (2)")
#st.write("### (4) show three metrics (https://docs.streamlit.io/library/api-reference/data/st.metric) for the selected items in (2): total sales, total profit, and overall profit margin (%)")
st.write("### (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)")

# (1): add a drop down for Category
select_options=df["Category"].unique()
category=st.selectbox(label="Choose a Category", options=select_options)

# (2): add a multi-select for Sub_Category
cat_subcat=df[["Category","Sub_Category"]].drop_duplicates().sort_values(by=["Category", "Sub_Category"]).reset_index(drop=True)
subcats_furniture=cat_subcat["Sub_Category"].where(cat_subcat["Category"]=="Furniture").dropna()
subcats_officesupplies=cat_subcat["Sub_Category"].where(cat_subcat["Category"]=="Office Supplies").dropna()
subcats_technology=cat_subcat["Sub_Category"].where(cat_subcat["Category"]=="Technology").dropna()
multiselect_options_map={
    "Furniture":subcats_furniture,
    "Office Supplies":subcats_officesupplies,
    "Technology":subcats_technology
    }
multiselect_options=multiselect_options_map.get(category, [])
subcategory=st.multiselect(label="Choose a Subcategory", options=multiselect_options)

# (3): show a line chart of sales for the selected items in (2)
selected_sales_by_month=df.where(df["Sub_Category"].isin(subcategory)).filter(items=['Sales']).dropna().groupby(pd.Grouper(freq='ME')).sum()
st.line_chart(selected_sales_by_month, y="Sales")

# (4): show three metrics for the selected items in (2): total sales, total profit, and overall profit margin (%)
# (5): use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)
sales_calc=round((df.where(df["Sub_Category"].isin(subcategory)).filter(items=['Sales']).dropna().sum())["Sales"],2)
selected_total_sales=st.metric(label="Total sales for selected subcategories:", value=f"${sales_calc}")
profit_calc=round((df.where(df["Sub_Category"].isin(subcategory)).filter(items=['Profit']).dropna().sum())["Profit"],2)
selected_total_profit=st.metric(label="Total profit for selected subcategories:", value=f"${profit_calc}")
margin_calc=round((profit_calc/sales_calc)*100,2)
total_overall_margin_calc=round(((df.filter(items=['Profit']).dropna().sum())["Profit"]/(df.filter(items=['Sales']).dropna().sum())["Sales"])*100,2)
margin_delta_calc=margin_calc-total_overall_margin_calc
selected_overall_margin=st.metric(label="Overall margin for selected subcategories:", value=f"{margin_calc}%", delta=margin_delta_calc)


