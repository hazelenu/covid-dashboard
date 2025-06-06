import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")
st.title("🌍 COVID-19 数据可视化面板")

# --- Load and clean data ---
data_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
@st.cache_data
def load_data():
    df = pd.read_csv(data_url)
    df = df[['location', 'date', 'total_cases', 'total_deaths', 'population']]
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna(subset=['total_cases'])
    return df

df = load_data()

# --- Country selection ---
countries = df['location'].unique()
country = st.selectbox("选择国家：", sorted(countries))

# --- Country stats function ---
def get_country_stats(df, country):
    country_df = df[df['location'] == country].copy()
    latest = country_df.sort_values('date').iloc[-1]
    total_cases = int(latest['total_cases'])
    total_deaths = int(latest['total_deaths']) if pd.notna(latest['total_deaths']) else 0
    death_rate = total_deaths / total_cases if total_cases > 0 else 0
    return total_cases, total_deaths, death_rate, country_df

cases, deaths, rate, country_df = get_country_stats(df, country)

# --- Display metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("累计确诊", f"{cases:,}")
col2.metric("累计死亡", f"{deaths:,}")
col3.metric("死亡率", f"{rate*100:.2f}%")

# --- Trend chart ---
fig = px.line(country_df, x='date', y='total_cases', title=f'{country} 疫情确诊趋势')
st.plotly_chart(fig, use_container_width=True)

# --- Bonus: Global case rate map ---
st.subheader("🌎 全球人均感染率地图")
latest_df = df.sort_values('date').groupby('location').last().reset_index()
latest_df['case_rate'] = latest_df['total_cases'] / latest_df['population']
fig_map = px.choropleth(
    latest_df,
    locations='location',
    locationmode='country names',
    color='case_rate',
    color_continuous_scale='Reds',
    title='各国人均感染率'
)
st.plotly_chart(fig_map, use_container_width=True)

st.caption("数据来源：Our World In Data")
