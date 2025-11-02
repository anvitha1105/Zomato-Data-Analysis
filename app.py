# app.py - minimal Streamlit app to preview your Zomato dataset
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Zomato Demo", layout="wide")
st.title("🍽 Zomato Restaurants - Demo")

@st.cache_data
def load_data():
    df = pd.read_csv("zomato.csv", encoding="latin-1")
    # minimal safe cleaning used for demo
    df = df.copy()
    # try to clean rating safely
    df['rate'] = df['rate'].astype(str).str.replace('/5', '').replace(['NEW','-','Not Rated'], pd.NA)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df['rate'] = df['rate'].fillna(df['rate'].mean())
    # clean cost column (remove commas) if present
    if 'approx_cost(for two people)' in df.columns:
        df['approx_cost(for two people)'] = (
            df['approx_cost(for two people)'].astype(str)
            .str.replace(',', '', regex=False)
        )
        df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
    return df

df = load_data()

st.subheader("Dataset preview (first 10 rows)")
st.dataframe(df.head(10))

st.markdown("### Quick charts")

# Simple bar: online order distribution (safe if column exists)
if 'online_order' in df.columns:
    fig1, ax1 = plt.subplots()
    sns.countplot(x='online_order', data=df, ax=ax1)
    ax1.set_title("Online Order Availability")
    st.pyplot(fig1)

# Top cuisines by count (safe if column exists)
if 'cuisines' in df.columns:
    top = df['cuisines'].value_counts().head(10)
    st.bar_chart(top)

st.success("Local demo loaded. Next: requirements.txt and deploy when you're ready.")
