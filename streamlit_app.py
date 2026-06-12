import streamlit as st
import pandas as pd
import math
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURAZIONE PROFESSIONALE ---
st.set_page_config(
    page_title='Executive GDP Intelligence',
    page_icon=':chart_with_upwards_trend:',
    layout="wide" # Fondamentale per il look Executive
)

# 1. Caricamento Dati (Manteniamo la tua funzione originale)
@st.cache_data
def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    MIN_YEAR, MAX_YEAR = 1960, 2022
    
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year', 'GDP'
    )
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

# 2. Logica Avanzata: Analizzatore di Anomalie (Nuovo!)
def detect_anomalies(df, threshold=2.5):
    # Calcoliamo la variazione percentuale annua per ogni paese
    df = df.sort_values(['Country Code', 'Year'])
    df['GDP_Change'] = df.groupby('Country Code')['GDP'].pct_change()
    
    # Identifichiamo anomalie statistiche (es. crolli o boom improvvisi)
    mean_change = df['GDP_Change'].mean()
    std_change = df['GDP_Change'].std()
    df['Is_Anomaly'] = (np.abs(df['GDP_Change'] - mean_change) > threshold * std_change)
    return df

# Inizializzazione dati
gdp_df = get_gdp_data()
gdp_df = detect_anomalies(gdp_df)

# --- SIDEBAR (Pulizia del layout) ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.info("Configura l'analisi executive")
    
    min_year, max_year = int(gdp_df['Year'].min()), int(gdp_df['Year'].max())
    from_year, to_year = st.slider('Periodo di Analisi', min_year, max_year, [2000, max_year])
    
    countries = gdp_df['Country Code'].unique()
    selected_countries = st.multiselect(
        'Seleziona Paesi Target',
        countries,
        ['DEU', 'FRA', 'GBR', 'ITA', 'USA', 'JPN'] # Aggiunta ITA per default
    )

# --- MAIN DASHBOARD (Executive Layout) ---
st.title("🌎 Global GDP Executive Intelligence")
st.markdown(f"**Analisi dinamica del PIL: {from_year} - {to_year}** | *Anomaly Detection Engine Active*")

# Metriche High-Level
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) & 
    (gdp_df['Year'] >= from_year) & (gdp_df['Year'] <= to_year)
]

cols = st.columns(len(selected_countries) if selected_countries else 1)
for i, country in enumerate(selected_countries):
    country_data = filtered_gdp_df[filtered_gdp_df['Country Code'] == country]
    if not country_data.empty:
        last_val = country_data['GDP'].iloc[-1] / 1e9
        prev_val = country_data['GDP'].iloc[0] / 1e9
        growth = ((last_val - prev_val) / prev_val) * 100
        cols[i % len(cols)].metric(f"{country}", f"${last_val:,.0f}B", f"{growth:+.1f}% Total")

st.divider()

# --- GRAFICO AVANZATO PLOTLY (L'effetto WOW) ---
st.subheader("📈 Analisi Traiettoria e Break Strutturali")

fig = px.line(filtered_gdp_df, x='Year', y='GDP', color='Country Code', 
              template="plotly_dark",

# Aggiungiamo i punti di Anomalia in rosso
anomalies = filtered_gdp_df[filtered_gdp_df['Is_Anomaly'] == True]
if not anomalies.empty:
    fig.add_trace(go.Scatter(
        x=anomalies['Year'], y=anomalies['GDP'],
        mode='markers',
        marker=dict(color='Crimson', size=8, symbol='x'),
        name='Anomalia Rilevata',
        hovertemplate="<b>Anomalia Economica</b><br>Anno: %{x}<br>Paese: %{text}",
        text=anomalies['Country Code']
    ))

fig.update_layout(hovermode="x unified", height=500)
st.plotly_chart(fig, use_container_width=True)

# --- ANALISI AUTOMATICA (Data Storytelling) ---
st.subheader("🔍 Executive Insights")
c1, c2 = st.columns(2)

with c1:
    st.write("**Eventi Significativi Rilevati:**")
    if not anomalies.empty:
        for _, row in anomalies.tail(3).iterrows():
            st.warning(f"⚠️ Shock rilevato in **{row['Country Code']}** nel **{row['Year']}** (Variazione: {row['GDP_Change']:.1%})")
    else:
        st.success("Nessuna anomalia strutturale rilevata nel periodo selezionato.")

with c2:
    st.write("**Analisi di Performance:**")
    top_country = filtered_gdp_df.groupby('Country Code')['GDP'].last().idxmax()
    st.info(f"La nazione con il PIL più alto nel {to_year} è **{top_country}**. L'algoritmo suggerisce stabilità per i mercati selezionati.")
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
