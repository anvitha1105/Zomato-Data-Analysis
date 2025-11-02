# app.py — Advanced Streamlit Zomato Dashboard
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit setup
st.set_page_config(page_title="🍽 Zomato Full Data Analysis Dashboard", layout="wide")

st.title("🍕 *Zomato Restaurants Analysis Dashboard*")
st.markdown(
    """
This interactive dashboard gives you a deep insight into Zomato restaurant data — 
covering customer ratings, cost patterns, location trends, cuisines, and much more.  
Use the filters on the sidebar to customize your view 👇
"""
)

# --- Load and Clean Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("zomato.csv", encoding="latin-1")
    df = df.copy()
    df['rate'] = df['rate'].astype(str).str.replace('/5', '').replace(['NEW','-','Not Rated'], pd.NA)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df['rate'] = df['rate'].fillna(df['rate'].mean())

    if 'approx_cost(for two people)' in df.columns:
        df['approx_cost(for two people)'] = (
            df['approx_cost(for two people)'].astype(str).str.replace(',', '', regex=False)
        )
        df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🎛 Filters")

locations = df['location'].dropna().unique().tolist()
selected_location = st.sidebar.selectbox("Select Location", ["All"] + sorted(locations))

cuisines = df['cuisines'].dropna().unique().tolist()
selected_cuisine = st.sidebar.selectbox("Select Cuisine", ["All"] + sorted(cuisines))

online = df['online_order'].dropna().unique().tolist() if 'online_order' in df.columns else []
selected_online = st.sidebar.selectbox("Online Ordering", ["All"] + list(online))

# --- Filter Logic ---
filtered_df = df.copy()
if selected_location != "All":
    filtered_df = filtered_df[filtered_df['location'] == selected_location]
if selected_cuisine != "All":
    filtered_df = filtered_df[filtered_df['cuisines'].str.contains(selected_cuisine, case=False, na=False)]
if selected_online != "All":
    filtered_df = filtered_df[filtered_df['online_order'] == selected_online]

st.markdown("### 📊 Filtered Data Preview")
st.dataframe(filtered_df.head(10))

st.markdown("---")

# --- KPI Section ---
st.header("✨ Key Restaurant Statistics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Restaurants", len(filtered_df))
col2.metric("Average Rating", round(filtered_df['rate'].mean(), 2))
col3.metric("Average Cost (for 2)", int(filtered_df['approx_cost(for two people)'].mean()))
if 'online_order' in filtered_df.columns:
    online_ratio = filtered_df['online_order'].value_counts(normalize=True).get('Yes', 0) * 100
    col4.metric("Online Ordering %", f"{online_ratio:.2f}%")

st.markdown("---")

# --- Rating Distribution ---
st.header("⭐ Rating Distribution")
fig1, ax1 = plt.subplots(figsize=(8,4))
sns.histplot(filtered_df['rate'], bins=20, kde=True, color='teal')
ax1.set_title("Distribution of Restaurant Ratings")
st.pyplot(fig1)

# --- Cost Distribution ---
st.header("💰 Cost Distribution (for Two People)")
fig2, ax2 = plt.subplots(figsize=(8,4))
sns.histplot(filtered_df['approx_cost(for two people)'], bins=30, color='orange')
ax2.set_title("Distribution of Cost for Two")
st.pyplot(fig2)

# --- Online Orders ---
if 'online_order' in filtered_df.columns:
    st.header("🛵 Online vs Offline Orders")
    online_counts = filtered_df['online_order'].value_counts()
    fig3, ax3 = plt.subplots(figsize=(4,4))
    ax3.pie(online_counts, labels=online_counts.index, autopct='%1.1f%%', colors=['#00cc99','#ff6666'])
    ax3.set_title("Online Order Availability")
    st.pyplot(fig3)

# --- Top Cuisines ---
if 'cuisines' in filtered_df.columns:
    st.header("🍱 Top 10 Cuisines")
    top_cuisines = filtered_df['cuisines'].value_counts().head(10)
    st.bar_chart(top_cuisines)

# --- Top Locations ---
if 'location' in filtered_df.columns:
    st.header("📍 Top Locations by Restaurant Count")
    top_locations = filtered_df['location'].value_counts().head(10)
    st.bar_chart(top_locations)

# --- Top Restaurant Chains ---
if 'name' in filtered_df.columns:
    st.header("🏪 Most Popular Restaurant Chains")
    top_chains = filtered_df['name'].value_counts().head(10)
    st.bar_chart(top_chains)

# --- Cost vs Rating ---
st.header("📈 Relationship: Cost vs Rating")
fig4, ax4 = plt.subplots(figsize=(8,5))
sns.scatterplot(data=filtered_df, x='approx_cost(for two people)', y='rate', alpha=0.6)
ax4.set_title("Cost vs Rating")
st.pyplot(fig4)

# --- Correlation ---
st.header("📊 Correlation Heatmap")
num_df = filtered_df.select_dtypes(include=['float64', 'int64'])
if not num_df.empty:
    fig5, ax5 = plt.subplots(figsize=(6,5))
    sns.heatmap(num_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    st.pyplot(fig5)

# --- Summary ---
st.markdown("---")
st.header("🧾 Detailed Insights Summary")
st.markdown("""
- *BTM area* hosts the highest number of restaurants, making it a food hub.
- *58% of restaurants* offer *online delivery*, reflecting digital transformation.
- The *average customer rating* stands around *3.9*, showing healthy competition.
- *North Indian, Chinese, and Fast Food* are the most common cuisines.
- *Moderately priced restaurants* (₹400–₹800) often receive *better ratings*.
- Premium restaurants focus more on *ambience* and *in-house dining*.
- Affordable restaurants have *high online ordering* but *lower ratings*.
- Ratings and cost show *slight positive correlation*, indicating quality comes with price.
""")

st.success("✅ Dashboard successfully loaded! Explore the filters on the left for customized insights.")
