import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="B2B Payments Dashboard",
    page_icon="💳",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("b2b_payment_dataset_1000.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert dates
    df["Due_Date"] = pd.to_datetime(df["Due_Date"], errors="coerce")
    df["Payment_Date"] = pd.to_datetime(df["Payment_Date"], errors="coerce")

    # Ensure numeric columns
    df["Invoice_Amount"] = pd.to_numeric(df["Invoice_Amount"], errors="coerce")
    df["Delay_Days"] = pd.to_numeric(df["Delay_Days"], errors="coerce")

    return df

df = load_data()

st.title("B2B Payment Dashboard")
st.markdown("Interactive dashboard for tracking invoices, payments, delays, and revenue collection.")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

region_options = ["All"] + sorted(df["Region"].dropna().unique().tolist())
status_options = ["All"] + sorted(df["Payment_Status"].dropna().unique().tolist())
client_options = ["All"] + sorted(df["Client_Name"].dropna().unique().tolist())

selected_region = st.sidebar.selectbox("Region", region_options)
selected_status = st.sidebar.selectbox("Payment Status", status_options)
selected_client = st.sidebar.selectbox("Client", client_options)

filtered_df = df.copy()

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

if selected_status != "All":
    filtered_df = filtered_df[filtered_df["Payment_Status"] == selected_status]

if selected_client != "All":
    filtered_df = filtered_df[filtered_df["Client_Name"] == selected_client]

# -----------------------------
# KPI Cards
# -----------------------------
total_invoices = filtered_df["Invoice_ID"].nunique()

paid_df = filtered_df[filtered_df["Payment_Status"].str.lower() == "paid"] if not filtered_df.empty else filtered_df
pending_df = filtered_df[filtered_df["Payment_Status"].str.lower() == "pending"] if not filtered_df.empty else filtered_df

paid_invoices = paid_df["Invoice_ID"].nunique()
pending_payments = pending_df["Invoice_ID"].nunique()
avg_delay_days = paid_df["Delay_Days"].dropna().mean() if not paid_df.empty else 0

st.subheader("KPI Cards")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Invoices", f"{total_invoices:,}")

with col2:
    st.metric("Paid Invoices", f"{paid_invoices:,}")

with col3:
    st.metric("Pending Payments", f"{pending_payments:,}")

with col4:
    st.metric("Average Delay Days", f"{avg_delay_days:.2f}")

# -----------------------------
# Charts Section
# -----------------------------
st.subheader("Visualizations")

chart_col1, chart_col2 = st.columns(2)

# 1. Payments by Region
with chart_col1:
    payments_by_region = (
        paid_df.groupby("Region", as_index=False)["Invoice_Amount"]
        .sum()
        .sort_values("Invoice_Amount", ascending=False)
    )

    if not payments_by_region.empty:
        fig_region = px.bar(
            payments_by_region,
            x="Region",
            y="Invoice_Amount",
            title="Payments by Region",
            text_auto=".2s"
        )
        fig_region.update_layout(xaxis_title="Region", yaxis_title="Paid Amount")
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info("No data available for Payments by Region.")

# 2. Delay Trend Analysis
with chart_col2:
    delay_trend = paid_df.dropna(subset=["Payment_Date", "Delay_Days"]).copy()
    if not delay_trend.empty:
        delay_trend["Payment_Month"] = delay_trend["Payment_Date"].dt.to_period("M").astype(str)
        delay_summary = (
            delay_trend.groupby("Payment_Month", as_index=False)["Delay_Days"]
            .mean()
            .sort_values("Payment_Month")
        )

        fig_delay = px.line(
            delay_summary,
            x="Payment_Month",
            y="Delay_Days",
            markers=True,
            title="Delay Trend Analysis"
        )
        fig_delay.update_layout(xaxis_title="Payment Month", yaxis_title="Average Delay Days")
        st.plotly_chart(fig_delay, use_container_width=True)
    else:
        st.info("No data available for Delay Trend Analysis.")

chart_col3, chart_col4 = st.columns(2)

# 3. Invoice Status Distribution
with chart_col3:
    status_dist = (
        filtered_df["Payment_Status"]
        .value_counts()
        .reset_index()
    )
    status_dist.columns = ["Payment_Status", "Count"]

    if not status_dist.empty:
        fig_status = px.pie(
            status_dist,
            names="Payment_Status",
            values="Count",
            title="Invoice Status Distribution",
            hole=0.4
        )
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No data available for Invoice Status Distribution.")

# 4. Revenue Collection Trend
with chart_col4:
    revenue_trend = paid_df.dropna(subset=["Payment_Date"]).copy()
    if not revenue_trend.empty:
        revenue_trend["Payment_Month"] = revenue_trend["Payment_Date"].dt.to_period("M").astype(str)
        revenue_summary = (
            revenue_trend.groupby("Payment_Month", as_index=False)["Invoice_Amount"]
            .sum()
            .sort_values("Payment_Month")
        )

        fig_revenue = px.area(
            revenue_summary,
            x="Payment_Month",
            y="Invoice_Amount",
            title="Revenue Collection Trend"
        )
        fig_revenue.update_layout(xaxis_title="Payment Month", yaxis_title="Collected Revenue")
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("No data available for Revenue Collection Trend.")

# -----------------------------
# Data Preview
# -----------------------------
st.subheader("Filtered Data Preview")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# Summary Section
# -----------------------------
st.subheader("Quick Insights")

total_amount = filtered_df["Invoice_Amount"].sum()
paid_amount = paid_df["Invoice_Amount"].sum() if not paid_df.empty else 0
pending_amount = pending_df["Invoice_Amount"].sum() if not pending_df.empty else 0

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Invoice Amount", f"{total_amount:,.2f}")
with c2:
    st.metric("Paid Amount", f"{paid_amount:,.2f}")
with c3:
    st.metric("Pending Amount", f"{pending_amount:,.2f}")

st.markdown("---")
st.caption("Dashboard developed in Streamlit using the uploaded B2B payments dataset.")
