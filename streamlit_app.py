py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path 

# --- 1. BRANDING & CONFIG (Stile rgandja.com) ---
st.set_page_config(layout="wide", page_title="Executive GDP Intelligence", page_icon=':chart_with_upwards_trend:')

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #E3B341; }
    div[data-testid="stMetric"] { background-color: #1C2128; border: 1px solid #30363D; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (Salvato e Ottimizzato) ---
@st.cache_data
def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    # Estraiamo anche i nomi per la mappa
    gdp_df = raw_gdp_df.melt(['Country Code', 'Country Name'], [str(x) for x in range(1960, 2023)], 'Year', 'GDP')
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

gdp_df = get_gdp_data()

# --- 3. SIDEBAR & DOWNLOAD (Funzionalità Avanzata) ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    from_year, to_year = st.slider('Timeline', 1960, 2022, [2000, 2022])
    countries = gdp_df['Country Code'].unique()
    selected_countries = st.multiselect('Target Countries', countries, ['ITA', 'USA', 'DEU', 'FRA'])
    
    # TASTO DOWNLOAD CSV
    csv_data = gdp_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Data (CSV)", data=csv_data, file_name='gdp_export.csv', mime='text/csv')

# --- 4. MAPPA MONDIALE (Novità!) ---
st.title("🌎 Global Economic Footprint")
map_year_df = gdp_df[gdp_df['Year'] == to_year]
fig_map = px.choropleth(map_year_df, locations="Country Code", color="GDP", hover_name="Country Name",
                        color_continuous_scale=px.colors.sequential.Goldred, template="plotly_dark")
fig_map.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# --- 5. ANALISI E PREVISIONI (Trendline integrata) ---
st.header("📈 Economic Trajectory & Forecasting")
filtered_df = gdp_df[(gdp_df['Country Code'].isin(selected_countries)) & (gdp_df['Year'] >= from_year) & (gdp_df['Year'] <= to_year)]

fig_line = px.scatter(filtered_df, x="Year", y="GDP", color="Country Code", 
                     trendline="lowess", # Previsione statistica
                     template="plotly_dark")
st.plotly_chart(fig_line, use_container_width=True)

# --- 6. INSIGHTS AUTOMATICI (L'effetto WOW) ---
st.subheader("💡 Intelligence Reports")
c1, c2 = st.columns(2)
with c1:
    if 'ITA' in selected_countries:
        ita_data = filtered_df[filtered_df['Country Code'] == 'ITA']
        growth = ((ita_data['GDP'].iloc[-1] - ita_data['GDP'].iloc[0]) / ita_data['GDP'].iloc[0]) * 100
        st.metric("Performance Italia", f"{growth:+.1f}%", "Nel periodo scelto")
with c2:
    top_country = filtered_df.groupby('Country Code')['GDP'].last().idxmax()
    st.info(f"**Leader di Mercato:** {top_country} detiene attualmente il PIL più alto nella tua selezione.")
