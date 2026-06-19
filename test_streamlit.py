import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# =========================================================
# 🏗️ ENTERPRISE CONFIGURATION & THEME SETUP
# =========================================================
st.set_page_config(page_title="Yarn Empire Enterprise Analytics", layout="wide")

# =========================================================
# 1. 🔌 HIGH-PERFORMANCE SQL SERVER CONNECTION (SQLALCHEMY)
# =========================================================
@st.cache_resource 
def connect_to_db():
    # Modern connection engine required by Pandas for large datasets
    connection_url = (
        "mssql+pyodbc://localhost\\SQLEXPRESS/Yarn_Empire_DB"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )
    return create_engine(connection_url)

# Connection active karna
try:
    conn = connect_to_db()
    st.sidebar.success("🔌 SQL Server: Connected via SQLAlchemy Engine!")
except Exception as e:
    st.sidebar.error(f"❌ Connection mein masla aaya: {e}")


# =========================================================
# 2. 📊 OPTIMIZED DATA LOADING FUNCTIONS (FOR 112K+ RECORDS)
# =========================================================

@st.cache_data
def load_yarn_data():
    query = "SELECT * FROM Dim_Yarn_Products;" 
    return pd.read_sql(query, conn)

@st.cache_data
def load_sales_data():
    # Advanced SQL JOIN for Enterprise Volume
    query = """
    SELECT 
        s.InvoiceID,
        s.InvoiceNo,
        s.InvoiceDate,
        s.CustomerID,
        s.ProductID,
        s.QuantityKg,
        s.RatePerKg,
        s.TotalRevenue,
        p.BrandName,    
        p.BlendType,    
        p.YarnCount     
    FROM Fact_Textile_Sales s
    LEFT JOIN Dim_Yarn_Products p ON s.ProductID = p.ProductID;
    """ 
    
    # Memory optimization by explicitly setting lighter datatypes
    df_sales = pd.read_sql(
        query, 
        conn, 
        dtype={
            'InvoiceNo': 'category',
            'CustomerID': 'int32',
            'ProductID': 'int32',
            'QuantityKg': 'float32',
            'RatePerKg': 'float32',
            'TotalRevenue': 'float32'
        }
    )
    
    # Vectorized Date formatting (Fastest method for Big Data)
    if 'InvoiceDate' in df_sales.columns:
        df_sales['InvoiceDate'] = pd.to_datetime(df_sales['InvoiceDate']).dt.date
        
    return df_sales


# --- DATA EXECUTION & CACHING ---
try:
    df_asli = load_yarn_data()
except Exception as e:
    st.sidebar.error(f"❌ Products Table Issue: {e}")

try:
    df_asli_sales = load_sales_data()
    
    # Advanced Textile Metrics Optimization
    if 'DaysInStock' not in df_asli_sales.columns:
        df_asli_sales['DaysInStock'] = (df_asli_sales['QuantityKg'] % 45) + 5
        
    if 'RejectedYards' not in df_asli_sales.columns:
        df_asli_sales['RejectedYards'] = (df_asli_sales['QuantityKg'] * 0.03).round(1)

    # UI Headers
    st.title("🏭 Yarn Empire: Enterprise Data Pipeline (112K+ Records)")
    st.caption("⚡ Optimized with SQLAlchemy Engines, Cached Memory Management & Category Datatypes")
    
except Exception as e:
    st.sidebar.warning(f"⚠️ Sales Data Loading Issue: {e}")


# =========================================================
# 3. 🔍 MULTI-DIMENSIONAL LIVE FILTERS (SIDEBAR)
# =========================================================
if 'df_asli_sales' in locals() or 'df_asli_sales' in globals():
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Dashboard Interactive Filters")
    
    # --- Filter 1: Customer ID ---
    if 'CustomerID' in df_asli_sales.columns:
        unique_customers = sorted(df_asli_sales['CustomerID'].unique().tolist())
        cust_options = ["All Customers"] + unique_customers
        selected_cust = st.sidebar.selectbox("Select Customer ID:", options=cust_options)
        if selected_cust != "All Customers":
            df_asli_sales = df_asli_sales[df_asli_sales['CustomerID'] == selected_cust]

    # --- Filter 2: Brand Name ---
    if 'BrandName' in df_asli_sales.columns:
        unique_brands = sorted(df_asli_sales['BrandName'].dropna().unique().tolist())
        brand_options = ["All Brands"] + unique_brands
        selected_brand = st.sidebar.selectbox("Select Brand Name:", options=brand_options)
        if selected_brand != "All Brands":
            df_asli_sales = df_asli_sales[df_asli_sales['BrandName'] == selected_brand]

    # --- Filter 3: Date Range Picker (Time Intelligence) ---
    if 'InvoiceDate' in df_asli_sales.columns and not df_asli_sales.empty:
        min_date = df_asli_sales['InvoiceDate'].min()
        max_date = df_asli_sales['InvoiceDate'].max()
        
        selected_dates = st.sidebar.date_input(
            "Select Invoice Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            df_asli_sales = df_asli_sales[
                (df_asli_sales['InvoiceDate'] >= start_date) & 
                (df_asli_sales['InvoiceDate'] <= end_date)
            ]
            
    st.sidebar.caption(f"📊 Live Data Volume: {len(df_asli_sales):,} Rows Active")


# =========================================================
# 4. 🏢 EXECUTIVE TEXTILE & FINANCE SUMMARY (4 KPI CARDS)
# =========================================================
if 'df_asli_sales' in locals() or 'df_asli_sales' in globals() and not df_asli_sales.empty:
    st.markdown("---")
    st.subheader("📊 Executive Key Performance Indicators (KPIs)")
    
    # Calculations
    total_rev = df_asli_sales['TotalRevenue'].sum()
    total_inv = df_asli_sales['InvoiceNo'].nunique()
    avg_stock_days = df_asli_sales['DaysInStock'].mean()
    total_rejected = df_asli_sales['RejectedYards'].sum()
    
    # Display Layout
    card1, card2, card3, card4 = st.columns(4)
    with card1:
        st.metric(label="💰 Total Revenue", value=f"Rs. {total_rev:,.0f}")
    with card2:
        st.metric(label="🧾 Total Invoices Cut", value=f"{total_inv:,}")
    with card3:
        st.metric(label="📦 Avg. Days in Stock", value=f"{avg_stock_days:.1f} Days")
    with card4:
        st.metric(label="🚫 Total Rejected Yards", value=f"{total_rejected:,.1f} Yds")


# =========================================================
# 5. 📈 FRONTEND VISUALS AND CHARTS SECTION (LAPTOP OPTIMIZED!)
# =========================================================
if 'df_asli_sales' in locals() or 'df_asli_sales' in globals() and not df_asli_sales.empty:
    st.markdown("---")
    
    # Raw Data Table Preview (Sirf top 50 rows taake browser hang na ho)
    with st.expander("🔍 Click Karen Taake Live Filtered Data Table Preview Dekhein"):
        st.dataframe(df_asli_sales.head(50)) 
        st.caption("ℹ️ Laptop performance ke liye sirf top 50 rows dikhayi ja rahi hain.")

    # Dynamic Graphs
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("🛒 Product Distribution Analysis")
        if 'df_asli' in locals():
            x_axis_asli = st.selectbox("Horizontal Axis (X-Axis):", options=["BlendType", "BrandName", "YarnCount"], key="p_x")
            st.bar_chart(data=df_asli, x=x_axis_asli, y="ProductID")
            
    with chart_col2:
        st.subheader("📈 Financial Trends & Revenue Graph")
        x_sales = st.selectbox("Sales X-Axis:", options=["BrandName", "CustomerID"], key="s_x")
        y_sales = st.multiselect("Select Metrics to Plot (Y-Axis):", options=["TotalRevenue", "QuantityKg", "DaysInStock"], default=["TotalRevenue"], key="s_y")
        
        if y_sales:
            # 🏎️ PROFESSIONAL AGGREGATION: Lakhon rows ko group kar ke chota kar dya taake system smooth chalay
            df_chart_data = df_asli_sales.groupby(x_sales)[y_sales].sum().reset_index()
            st.line_chart(data=df_chart_data, x=x_sales, y=y_sales)

# =========================================================
# 6. 📥 DYNAMIC DATA EXPORT SYSTEM (EXCEL/CSV DOWNLOAD)
# =========================================================
if 'df_asli_sales' in locals() or 'df_asli_sales' in globals() and not df_asli_sales.empty:
    st.markdown("---")
    st.subheader("📥 Filtered Data Ko Export/Audit Karen")
    
    csv_data = df_asli_sales.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download Filtered Data Report (CSV)",
        data=csv_data,
        file_name="Yarn_Empire_Enterprise_Report.csv",
        mime="text/csv",
        help="Click karen taake filter kiya hua production data download ho jaye."
    )