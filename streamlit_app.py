import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression

# --- 0. CONFIGURAZIONE FILE ---
DATA_FILENAME = "data/gdp_data.csv"  # ✅ Percorso CORRETTO!

# --- 1. CONFIGURAZIONE E BRANDING (Stile rgandja.com) ---
st.set_page_config(layout="wide", page_title="RGandja | GDP Intelligence", page_icon='📈')

st.markdown("""
    <style>
    /* Sfondo e Testi */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #E3B341; }
    
    /* Box Metriche */
    div[data-testid="stMetric"] { 
        background-color: #1C2128; 
        border: 1px solid #30363D; 
        padding: 15px; 
        border-radius: 10px; 
    }
    
    /* Personalizzazione Slider */
    .stSlider > div > div > div > div { background-color: #E3B341 !important; }
    
    /* Header Brand */
    .brand-text { 
        font-size: 2.2rem; 
        font-weight: bold; 
        font-family: 'Playfair Display', serif; 
        color: #E3B341; 
        margin-left: 15px; 
    }
    
    /* Pulizia Interfaccia */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. HEADER BRANDIZZATO
col_logo, col_title = st.columns([1, 8])
with col_logo:
    try:
        st.image("logo.png", width=80)
    except:
        st.write("📈")

with col_title:
    st.markdown('<span class="brand-text">RGandja | Global Economic Intelligence</span>', unsafe_allow_html=True)

# --- 3. DATA ENGINE (Logica Originale + Ottimizzazione) ---
@st.cache_data
def get_gdp_data():
    """Carica e pulisce i dati dal file CSV locale"""
    try:
        raw_gdp_df = pd.read_csv(DATA_FILENAME)
        # Trasformiamo le colonne degli anni in righe (Pivot)
        gdp_df = raw_gdp_df.melt(
            ['Country Code', 'Country Name'], 
            [str(x) for x in range(1960, 2026)], 
            var_name='Year',
            value_name='GDP'
        )
        gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
        gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce')
        return gdp_df
    except FileNotFoundError:
        st.error(f"❌ File '{DATA_FILENAME}' non trovato!")
        return None

# --- 4. ANALIZZATORE DI ANOMALIE (Intelligenza Artificiale) ---
def detect_anomalies(df, threshold=2.5):
    """Rileva shock economici improvvisi usando lo Z-Score"""
    if df is None:
        return None
    df = df.sort_values(['Country Code', 'Year'])
    df['GDP_Change'] = df.groupby('Country Code')['GDP'].pct_change()
    mean_val = df['GDP_Change'].mean()
    std_val = df['GDP_Change'].std()
    df['Is_Anomaly'] = (np.abs(df['GDP_Change'] - mean_val) > threshold * std_val)
    return df

# Inizializzazione Dati
gdp_df = get_gdp_data()
if gdp_df is None:
    st.stop()
gdp_df = detect_anomalies(gdp_df)

# --- 5. SIDEBAR (Control Panel Brandizzato) ---
with st.sidebar:
    try:
        st.image("logo.png", width=120)
    except:
        pass
    st.title("RGandja Admin")
    st.caption("Strategic Decision Support Tool")
    st.divider()
    
    st.subheader("⚙️ Filtri Analisi")
    min_y, max_y = int(gdp_df['Year'].min()), int(gdp_df['Year'].max())
    from_year, to_year = st.slider('Periodo Temporale', min_y, max_y, [2000, max_y])
    
    available_countries = sorted(gdp_df['Country Code'].unique())
    selected_countries = st.multiselect(
        'Paesi in Analisi', 
        available_countries, 
        ['ITA', 'USA', 'DEU', 'FRA', 'CHN']
    )

    st.subheader("🎯 Focus Paese")
    focus_country = st.selectbox(
    "Seleziona il Paese Focus",
    available_countries,
    index=0
    )

    st.divider()
    
    # Esportazione Dati (Funzionalità Avanzata)
    csv_report = gdp_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica Report Dati (CSV)", data=csv_report, file_name='rgandja_gdp_report.csv')

# --- 6. DASHBOARD INTERATTIVA ---
if not selected_countries:
    st.warning("⚠️ Seleziona almeno un paese per attivare l'analisi.")
else:
    # Filtro dati dinamico
    filtered_df = gdp_df[
        (gdp_df['Country Code'].isin(selected_countries)) & 
        (gdp_df['Year'] >= from_year) & 
        (gdp_df['Year'] <= to_year)
    ].dropna()

    # A. MAPPA MONDIALE (Effetto Wow)
    st.subheader("🌍 Asset Allocation Globale")
    map_year_data = gdp_df[gdp_df['Year'] == to_year].dropna()
    fig_map = px.choropleth(
        map_year_data, 
        locations="Country Code", 
        color="GDP", 
        hover_name="Country Name", 
        color_continuous_scale="YlOrRd",  # ✅ NUOVO
        template="plotly_dark"
    )
    fig_map.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # 🔄 Auto-refresh ogni 60 secondi (senza moduli esterni)
    st.markdown("""
    <script>
        setTimeout(function(){
            window.location.reload();
        }, 60000);
    </script>
    """, unsafe_allow_html=True)


    # B. ANALISI STORICA E SHOCK (Grafico Lineare)
    st.subheader("📈 Analisi Trend & Eventi Critici")
    fig_line = px.line(filtered_df, x="Year", y="GDP", color="Country Code", template="plotly_dark")
    
    # Inserimento Anomalie (Punti Rossi)
    anomalies_found = filtered_df[filtered_df['Is_Anomaly'] == True]
    if not anomalies_found.empty:
        fig_line.add_trace(go.Scatter(
            x=anomalies_found['Year'], 
            y=anomalies_found['GDP'], 
            mode='markers', 
            marker=dict(color='red', size=10, symbol='x'),
            name='Shock Economico'
        ))
    st.plotly_chart(fig_line, use_container_width=True)

    # C. EXECUTIVE INSIGHTS (Metriche Intelligenti)
    st.subheader("💡 Insights Strategici")
    c1, c2 = st.columns(2)
    with c1:
        if 'ITA' in selected_countries:
            ita_data = filtered_df[filtered_df['Country Code'] == 'ITA']
            if len(ita_data) > 1:
                total_growth = ((ita_data['GDP'].iloc[-1] - ita_data['GDP'].iloc[0]) / ita_data['GDP'].iloc[0]) * 100
                st.metric("Focus Italia", f"{total_growth:+.1f}%", "Crescita nel periodo")
    with c2:
        if not filtered_df.empty:
            leader = filtered_df.groupby('Country Code')['GDP'].last().idxmax()
            st.info(f"**Market Leader:** Nel {to_year}, il PIL più elevato è di **{leader}**.")

    # D. PREVISIONI FUTURE (Regressione Lineare)
    st.divider()
    st.subheader("🔮 Predictive Outlook: Prossimi 5 Anni")
    
    cp1, cp2 = st.columns([2, 1])
    with cp1:
        fig_pred = go.Figure()
        for country in selected_countries:
            c_full = gdp_df[gdp_df['Country Code'] == country].dropna()
            if len(c_full) > 1:
                X = c_full['Year'].values.reshape(-1, 1)
                y = c_full['GDP'].values
                
                # Machine Learning Model
                model = LinearRegression().fit(X, y)
                future = np.array(range(2023, 2028)).reshape(-1, 1)
                preds = model.predict(future)
                
                # Linea Storica
                fig_pred.add_trace(go.Scatter(x=c_full['Year'], y=y, name=f"{country} (Storico)"))
                # Linea Futura (Tratteggiata)
                fig_pred.add_trace(go.Scatter(
                    x=future.flatten(), 
                    y=preds, 
                    name=f"{country} (Forecasting)", 
                    line=dict(dash='dash')
                ))
            
        fig_pred.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_pred, use_container_width=True)
        
    with cp2:
        st.write("**Metodologia Predittiva**")
        st.caption("Proiezione calcolata tramite regressione lineare sui dati storici.")
        st.info("💡 Questo modulo stima la crescita potenziale basata sul trend strutturale, escludendo variabili geopolitiche imprevedibili.")
