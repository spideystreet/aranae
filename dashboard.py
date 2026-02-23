import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from services.db import get_db_connection

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Aranae - Job Analytics", page_icon="🕸️", layout="wide")

st.title("🕸️ Aranae - Job Analytics")
st.markdown("---")


@st.cache_data(ttl=600)
def load_data():
    conn = get_db_connection()
    # Join with source_metadata to get icons
    # We select specific columns to avoid duplicate 'source' column names
    query = """
        SELECT 
            j.publication_date, 
            j.title, 
            j.company, 
            j.city, 
            j.region, 
            j.salary, 
            j.tjm, 
            j.duration, 
            j.experience_level, 
            j.url as offer_url,
            m.icon_url as source
        FROM fct_jobs j
        LEFT JOIN sources_metadatas m ON j.source = m.source_name
    """
    df = pd.read_sql(query, conn)
    return df


try:
    df = load_data()

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Options")

    cities = st.sidebar.multiselect(
        "Select City", options=sorted(df["city"].dropna().unique()), default=[]
    )

    # Filter logic
    filtered_df = df.copy()
    if cities:
        filtered_df = filtered_df[filtered_df["city"].isin(cities)]

    # --- Key Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Offers", len(filtered_df))
    with col2:
        st.metric("Companies", filtered_df["company"].nunique())
    with col3:
        # Use raw string for regex
        avg_tjm_series = filtered_df["tjm"].dropna().astype(str).str.extract(r"(\d+)")
        if not avg_tjm_series.empty:
            avg_tjm = avg_tjm_series.astype(float).mean()
            st.metric("Avg TJM (Estimate)", f"{int(avg_tjm.iloc[0])} €")
        else:
            st.metric("Avg TJM (Estimate)", "N/A")
    with col4:
        st.metric("Cities", filtered_df["city"].nunique())

    st.markdown("---")

    # --- Charts ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Cities")
        city_counts = filtered_df["city"].value_counts().reset_index()
        city_counts.columns = ["city", "count"]
        fig_city = px.bar(
            city_counts.head(10),
            x="city",
            y="count",
            template="plotly_dark",
            color="count",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_city, use_container_width=True)

    with c2:
        st.subheader("Jobs Map placeholder")
        st.info("Additional visualizations can be added here (e.g., salary distribution).")

    # --- Data Table ---
    st.markdown("---")
    st.subheader("Latest Job Offers")

    # Reordering columns for better display
    display_cols = [
        "source",
        "publication_date",
        "title",
        "company",
        "city",
        "region",
        "salary",
        "tjm",
        "duration",
        "experience_level",
        "offer_url",
    ]

    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "source": st.column_config.ImageColumn("source", help="Job Platform Icon"),
            "offer_url": st.column_config.LinkColumn("offer_url", display_text="Open Offer"),
            "city": st.column_config.TextColumn("city"),
            "region": st.column_config.TextColumn("region"),
        },
    )

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Make sure the database is running and dbt models are built.")
