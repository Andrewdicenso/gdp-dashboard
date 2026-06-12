import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- 1. CONFIGURAZIONE E BRANDING ---
st.set_page_config(layout="wide", page_title="Executive GDP Intelligence", page_icon=':chart_with_upwards_trend:')

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #E3B341; }
    div[data-testid="stMetric"] { background-color: #1C2128; border: 1px solid #30363D; padding: 15px; border-radius: 10px; }
    .stSlider > div > div > div > div { background-color: #E3B341 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data
def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    # Pivot dei dati per avere Year e GDP come colonne
    gdp_df = raw_gdp_df.melt(['Country Code', 'Country Name'], [str(x) for x in range(1960, 2023)], 'Year', 'GDP')
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

# --- 3. ANALIZZATORE DI ANOMALIE (La parte "Intelligente") ---
def detect_anomalies(df, threshold=2.5):
    df = df.sort_values(['Country Code', 'Year'])
    df['GDP_Change'] = df.groupby('Country Code')['GDP'].pct_change()
    mean_val = df['GDP_Change'].mean()
    std_val = df['GDP_Change'].std()
    df['Is_Anomaly'] = (np.abs(df['GDP_Change'] - mean_val) > threshold * std_val)
    return df

# Inizializzazione
gdp_df = get_gdp_data()
gdp_df = detect_anomalies(gdp_df)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    from_year, to_year = st.slider('Timeline', 1960, 2022, [2000, 2022])
    countries = sorted(gdp_df['Country Code'].unique())
    selected_countries = st.multiselect('Target Countries', countries, ['ITA', 'USA', 'DEU', 'FRA'])
    
    st.divider()
    csv_data = gdp_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export CSV Report", data=csv_data, file_name='gdp_intelligence_report.csv', mime='text/csv')

# --- 5. MAIN DASHBOARD ---
st.title("🌎 Global Economic Intelligence")

if not selected_countries:
    st.warning("⚠️ Seleziona almeno un paese nella barra laterale per visualizzare l'analisi.")
else:
    # Filtro dati
    filtered_df = gdp_df[(gdp_df['Country Code'].isin(selected_countries)) & (gdp_df['Year'] >= from_year) & (gdp_df['Year'] <= to_year)]

    # A. MAPPA COROPLETICA
    st.subheader("Visualizzazione Asset Globali")
    map_df = gdp_df[gdp_df['Year'] == to_year]
    fig_map = px.choropleth(map_df, locations="Country Code", color="GDP", hover_name="Country Name",
                            color_continuous_scale=px.colors.sequential.Goldred, template="plotly_dark")
    fig_map.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # B. GRAFICO TREND + ANOMALIE
    st.subheader("📈 Traiettoria Economica & Forecasting")
    fig_line = px.line(filtered_df, x="Year", y="GDP", color="Country Code", template="plotly_dark")
    
    # Aggiunta punti anomalia
    anomalies = filtered_df[filtered_df['Is_Anomaly'] == True]
    if not anomalies.empty:
        fig_line.add_trace(go.Scatter(x=anomalies['Year'], y=anomalies['GDP'], mode='markers',
                                      marker=dict(color='red', size=10, symbol='x'), name='Shock Rilevato'))
    
    st.plotly_chart(fig_line, use_container_width=True)

    # C. INSIGHTS AUTOMATICI
    st.subheader("💡 Executive Summary")
    c1, c2 = st.columns(2)
    with c1:
        # Analisi Italia (se presente)
        if 'ITA' in selected_countries:
            ita_data = filtered_df[filtered_df['Country Code'] == 'ITA']
            if len(ita_data) > 1:
                growth = ((ita_data['GDP'].iloc[-1] - ita_data['GDP'].iloc[0]) / ita_data['GDP'].iloc[0]) * 100
                st.metric("Performance Italia", f"{growth:+.1f}%", "Crescita nel periodo")
    with c2:
        top_c = filtered_df.groupby('Country Code')['GDP'].last().idxmax()
        st.info(f"**Insight:** Il leader attuale è **{top_c}**. Sono stati rilevati {len(anomalies)} eventi di instabilità nel periodo.")** {top_country} detiene attualmente il PIL più alto nella tua selezione.")
