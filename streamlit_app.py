import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression

# --- 0. CONFIGURAZIONE FILE ---
DATA_FILENAME = "data/gdp_data.csv"

# --- 1. CONFIGURAZIONE E BRANDING ---
st.set_page_config(
    layout="wide", 
    page_title="RGandja | Global GDP Intelligence", 
    page_icon='📈',
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://rgandja.com',
        'About': "# RGandja Economic Dashboard\nAnalisi predittiva e monitoraggio del PIL globale."
    }
)

# Miglioramento SEO: Meta Description
st.markdown('<meta name="description" content="Dashboard economica RGandja: analisi in tempo reale del PIL mondiale e shock economici con modelli predittivi.">', unsafe_allow_html=True)

# FIX ACCESSIBILITÀ POTENZIATO: Risolve Zoom e Landmark (il segreto per il 100%)
st.components.v1.html(
    """
    <script>
        function fixA11y() {
            // Sblocca lo zoom su mobile
            const meta = window.parent.document.querySelector('meta[name="viewport"]');
            if (meta) meta.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes');
            
            // Definisce l'area principale per gli screen reader
            const main = window.parent.document.querySelector('section.main');
            if (main) main.setAttribute('role', 'main');
        }
        // Esegue il fix a intervalli per assicurarsi che Streamlit sia pronto
        fixA11y();
        [1000, 3000, 5000].forEach(t => setTimeout(fixA11y, t));
    </script>
    """,
    height=0,
)

st.markdown("""
    <style>
    /* Reset Layout per massima pulizia */
    .block-container { padding-top: 2rem !important; max-width: 90% !important; }
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Titoli Eleganti */
    h1, h2, h3 { 
        font-family: 'Playfair Display', serif; 
        color: #F0BC3E; 
        text-align: center;
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    /* Header Brandizzato */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 3rem;
    }
    .brand-text { font-size: 3rem; font-weight: bold; color: #F0BC3E; }

    /* Animazione "Sinuosa" - Glow Interno senza scrollbars */
    @keyframes subtle-glow {
        0% { filter: brightness(0.9) saturate(0.9); }
        50% { filter: brightness(1.2) saturate(1.2) drop-shadow(0 0 10px rgba(240, 188, 62, 0.4)); }
        100% { filter: brightness(0.9) saturate(0.9); }
    }

    /* Applica l'animazione solo al contenuto del grafico */
    .js-plotly-plot {
        animation: subtle-glow 5s infinite ease-in-out;
        border-radius: 20px;
    }
    
    /* Rimuove le barre di scorrimento fastidiose */
    .element-container, .stPlotlyChart { overflow: hidden !important; }
    
    #MainMenu, footer { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- CARICAMENTO LOGO (Aggiungi questo pezzo!) ---
import base64

def get_base64_img(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

img_b64 = get_base64_img("logo.png")
if img_b64:
    logo_html = f'<img src="data:image/png;base64,{img_b64}" width="60" style="vertical-align: middle;">'
else:
    logo_html = '<span style="font-size: 50px;">📈</span>'

# --- 2. HEADER BRANDIZZATO (Ora funzionerà!) ---
st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 20px; margin-bottom: 10px;">
        {logo_html}
        <span class="brand-text" style="margin: 0; padding: 0; line-height: 1;">RGandja</span>
    </div>
    <h2 style='text-align: center; margin-top: 0;'>Global Economic Intelligence</h2>
""", unsafe_allow_html=True)

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
        # Aggiunto help per accessibilità
        st.image("logo.png", width=50, help="Logo RGandja")
    except:
        pass
    st.title("RGandja")
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
        index=available_countries.index("ITA") if "ITA" in available_countries else 0
    )

    st.divider()

    # Esportazione Dati ottimizzata senza funzioni nidificate nella sidebar
    st.download_button(
        label="📥 Scarica Report Dati (CSV)",
        data=gdp_df.to_csv(index=False).encode('utf-8'),
        file_name='rgandja_gdp_report.csv',
        mime='text/csv',
        help="Clicca per scaricare i dati completi in formato CSV"
    )

# --- 6. DASHBOARD INTERATTIVA (Mappa Centrata) ---
if not selected_countries:
    st.warning("⚠️ Seleziona almeno un paese per attivare l'analisi.")
else:
    # Filtro dati dinamico
    filtered_df = gdp_df[
        (gdp_df['Country Code'].isin(selected_countries)) &
        (gdp_df['Year'] >= from_year) &
        (gdp_df['Year'] <= to_year)
    ].dropna()
    
    # --- A. MAPPA MONDIALE ---
    map_year_data = gdp_df[gdp_df['Year'] == to_year].dropna()

    fig_map = px.choropleth(
        map_year_data, 
        locations="Country Code", 
        color="GDP", 
        hover_name="Country Name", 
        color_continuous_scale=["#1C2128", "#E3B341", "#F0BC3E"], # Scala dorata premium
        template="plotly_dark"
    )

    fig_map.update_layout(
        height=700, # Più grande e d'impatto
        margin={"r":10,"t":10,"l":10,"b":10},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)'
        )   
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.divider()

    # B. ANALISI STORICA E SHOCK (Grafico Lineare - Allineato dentro l'else)
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

# --- C. MERCATO AZIONARIO REAL TIME ---
st.subheader("📊 Mercato Azionario R.T.")
try:
    import yfinance as yf
    @st.cache_data(ttl=300)
    def get_market_data():
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "EURUSD=X", "BTC-USD"]
        data = []
        for t in tickers:
            s = yf.Ticker(t)
            # Prezzo e variazione semplificati per stabilità
            hist = s.history(period="2d")
            if len(hist) > 1:
                last_p = hist['Close'].iloc[-1]
                change = ((last_p - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                data.append({"Asset": t, "Prezzo": f"{last_p:.2f}", "Var %": change})
        return pd.DataFrame(data)

    m_df = get_market_data()
    # Visualizzazione orizzontale a colonne per richiamare i board finanziari
    cols = st.columns(len(m_df))
    for i, row in m_df.iterrows():
        color = "normal" if row['Var %'] > 0 else "inverse"
        cols[i].metric(row['Asset'], row['Prezzo'], f"{row['Var %']:+.2f}%", delta_color=color)
except:
    st.info("Dati di mercato momentaneamente non disponibili")

    # --- D. PREVISIONI E INSIGHTS (Versione Corretta e Sinuosa) ---
    st.divider()
    cp1, cp2 = st.columns([2, 1])

    with cp1:
        st.subheader("🔮 Predictive Outlook: Prossimi 5 Anni")
        
        # 1. Inizializzazione del Grafico (Indispensabile per evitare l'errore)
        fig_pred = go.Figure()
        
        for country in selected_countries:
            c_full = gdp_df[gdp_df['Country Code'] == country].dropna()
            if len(c_full) > 1:
                X = c_full['Year'].values.reshape(-1, 1)
                y = c_full['GDP'].values
                model = LinearRegression().fit(X, y)
                future = np.array(range(2026, 2031)).reshape(-1, 1)
                preds = model.predict(future)
                
                fig_pred.add_trace(go.Scatter(x=c_full['Year'], y=y, name=f"{country} (Storico)"))
                fig_pred.add_trace(go.Scatter(
                    x=[int(year) for year in future.flatten()],
                    y=preds, 
                    name=f"{country} (Forecasting)", 
                    line=dict(dash='dash')
                ))
            
        fig_pred.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_pred, use_container_width=True)
        
        # SPIEGAZIONE ESTESA SOTTO IL GRAFICO
        st.markdown("""
            <div style="text-align: justify; color: #808495; font-size: 0.95rem; margin-top: 20px; 
                        border-left: 3px solid #F0BC3E; padding-left: 15px; line-height: 1.6; clear: both;">
                <strong>Metodologia Predittiva:</strong> Proiezione calcolata tramite regressione lineare sui dati storici. 
                Questo modulo stima la crescita potenziale basata sul trend strutturale, escludendo variabili geopolitiche 
                imprevedibili che potrebbero alterare il percorso economico nel breve termine.
            </div>
        """, unsafe_allow_html=True)

    with cp2:
        # 1. Calcolo del valore del Leader
        leader_name = filtered_df.groupby('Country Code')['GDP'].last().idxmax() if not filtered_df.empty else "N/A"

        # 2. Titolo Bianco superiore
        st.markdown("<h3 style='text-align: center; color: #FFFFFF; margin-top: -10px; margin-bottom: 30px;'>💡 Focus & Leadership</h3>", unsafe_allow_html=True)
        
        # 3. Recupero dati per la crescita
        focus_data = filtered_df[filtered_df['Country Code'] == focus_country]
        if len(focus_data) > 1:
            total_growth = ((focus_data['GDP'].iloc[-1] - focus_data['GDP'].iloc[0]) / focus_data['GDP'].iloc[0]) * 100
            
            # NOTA: Tutto il contenuto grafico è dentro questa f-string
            st.markdown(f"""
                <div style="text-align: center; background-color: #161B22; padding: 20px; border-radius: 15px; border: 1px solid #30363D; margin-top: 50px;">
                    <p style="margin: 0; color: #F0BC3E; font-size: 1.1rem; font-weight: bold; line-height: 1;">Focus {focus_country}</p>
                    <h2 style="margin: 5px 0; color: #2ecc71; font-size: 1.8rem; font-weight: bold; line-height: 1;">{total_growth:+.1f}%</h2>
                    <p style="margin: 0; color: #2ecc71; font-size: 0.85rem; opacity: 0.9; line-height: 1;">Crescita nel periodo</p>
                    
                    <hr style="border: 0; border-top: 1px solid #30363D; margin: 15px 0;">
                    
                    <p style="margin: 0; color: #F0BC3E; font-size: 1rem; font-weight: bold; line-height: 1;">Market Leader nel {to_year}</p>
                    <p style="margin: 5px 0 0 0; color: #FFFFFF; font-size: 1.1rem; line-height: 1.1;">Il PIL più elevato è di <strong>{leader_name}</strong></p>
                </div>
            """, unsafe_allow_html=True)

    # --- FOOTER TECNICO (Estratto dalle colonne per stare a fondo pagina) ---
    st.divider()
    st.caption("© 2026 RGandja | Data Intelligence Unit")

# --- FINE DEL CODICE ---