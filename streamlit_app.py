import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression
import base64

# --- 0. CONFIGURAZIONE FILE ---
DATA_FILENAME = "data/gdp_data.csv"

# --- 1. CONFIGURAZIONE E BRANDING ---
st.set_page_config(
    layout="wide", 
    page_title="RGandja | Global GDP Intelligence", 
    page_icon='📈',
    initial_sidebar_state="expanded"
)

# FIX ACCESSIBILITÀ E VIEWPORT
st.components.v1.html(
    """
    <script>
        function fixA11y() {
            const meta = window.parent.document.querySelector('meta[name="viewport"]');
            if (meta) meta.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes');
            const main = window.parent.document.querySelector('section.main');
            if (main) main.setAttribute('role', 'main');
        }
        fixA11y();
        [1000, 3000].forEach(t => setTimeout(fixA11y, t));
    </script>
    """,
    height=0,
)

# --- 2. CSS CUSTOM POTENZIATO (Include Gold Glow e Responsive Layout) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 92% !important; }
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Animazione Bagliore Oro per Risultati */
    @keyframes goldGlow {
        0% { text-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700; opacity: 0.9; }
        50% { text-shadow: 0 0 20px #ffd700, 0 0 35px #ffcc00; opacity: 1; }
        100% { text-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700; opacity: 0.9; }
    }
    .gold-glow-text {
        color: #FFD700 !important;
        animation: goldGlow 2.5s infinite ease-in-out;
        font-weight: bold;
    }

    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #F0BC3E; text-align: center; }
    .brand-text { font-size: 3rem; font-weight: bold; color: #F0BC3E; }
    
    /* Pulizia Grafici */
    .js-plotly-plot { border-radius: 15px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    
    #MainMenu, footer { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CARICAMENTO LOGO ---
def get_base64_img(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

img_b64 = get_base64_img("logo.png")
logo_html = f'<img src="data:image/png;base64,{img_b64}" width="60">' if img_b64 else '<span style="font-size: 50px;">📈</span>'

# --- 4. HEADER BRANDIZZATO ---
st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 10px; margin-bottom: 5px;">
        {logo_html}
        <span class="brand-text" style="line-height: 1;">RGandja</span>
    </div>
    <h2 style='text-align: center; margin-top: 0; font-size: 1.5rem; color: #FFFFFF; opacity: 0.8;'>Global Economic Intelligence</h2>
""", unsafe_allow_html=True)

# --- 5. DATA ENGINE (Caricamento e Analisi) ---
@st.cache_data
def get_gdp_data():
    try:
        raw_gdp_df = pd.read_csv(DATA_FILENAME)
        gdp_df = raw_gdp_df.melt(
            ['Country Code', 'Country Name'], 
            [str(x) for x in range(1960, 2026)], 
            var_name='Year', value_name='GDP'
        )
        gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
        gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce')
        return gdp_df
    except:
        st.error(f"❌ Errore nel caricamento del file {DATA_FILENAME}")
        return None

def detect_anomalies(df, threshold=2.5):
    if df is None: return None
    df = df.sort_values(['Country Code', 'Year'])
    df['GDP_Change'] = df.groupby('Country Code')['GDP'].pct_change()
    mean_val = df['GDP_Change'].mean()
    std_val = df['GDP_Change'].std()
    df['Is_Anomaly'] = (np.abs(df['GDP_Change'] - mean_val) > threshold * std_val)
    return df

# Inizializzazione Dati
gdp_df = get_gdp_data()
if gdp_df is None: st.stop()
gdp_df = detect_anomalies(gdp_df)

# --- 6. SIDEBAR (Control Panel) ---
with st.sidebar:
    st.title("RGandja")
    st.caption("Strategic Decision Support Tool")
    st.divider()
    
    st.subheader("⚙️ Filtri Analisi")
    min_y, max_y = int(gdp_df['Year'].min()), int(gdp_df['Year'].max())
    from_year, to_year = st.slider('Periodo Temporale', min_y, max_y, [2000, max_y])
    
    available_countries = sorted(gdp_df['Country Code'].unique())
    selected_countries = st.multiselect('Paesi in Analisi', available_countries, ['ITA', 'USA', 'DEU', 'FRA', 'CHN'])

    st.subheader("🎯 Focus Paese")
    focus_country = st.selectbox("Seleziona il Paese Focus", available_countries, 
                                 index=available_countries.index("ITA") if "ITA" in available_countries else 0)

    st.divider()
    st.download_button(label="📥 Report CSV", data=gdp_df.to_csv(index=False).encode('utf-8'), 
                       file_name='rgandja_report.csv', mime='text/csv')

# --- 7. DASHBOARD INTERATTIVA ---
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
        map_year_data, locations="Country Code", color="GDP", hover_name="Country Name", 
        color_continuous_scale=["#1C2128", "#E3B341", "#F0BC3E"], template="plotly_dark"
    )
    fig_map.update_layout(
        height=600, margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', bgcolor='rgba(0,0,0,0)')   
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.divider()

    # --- B. MERCATO AZIONARIO REAL TIME ---
    st.subheader("📊 Mercato Azionario RT")
    try:
        import yfinance as yf
        @st.cache_data(ttl=300)
        def get_market_data():
            tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "EURUSD=X", "BTC-USD"]
            data = []
            for t in tickers:
                s = yf.Ticker(t)
                hist = s.history(period="2d")
                if len(hist) > 1:
                    last_p = hist['Close'].iloc[-1]
                    change = ((last_p - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    data.append({"Asset": t, "Prezzo": f"{last_p:.2f}", "Var %": change})
            return pd.DataFrame(data)

        m_df = get_market_data()
        cols = st.columns(len(m_df))
        for i, row in m_df.iterrows():
            delta_color = "normal" if row['Var %'] > 0 else "inverse"
            cols[i].metric(row['Asset'], row['Prezzo'], f"{row['Var %']:+.2f}%", delta_color=delta_color)
    except:
        st.info("Dati di mercato momentaneamente non disponibili")

    st.divider()

    # --- C. LAYOUT AFFIANCATO: TREND (Sinistra) + FOCUS & LEADERSHIP (Destra) ---
    col_left, col_right = st.columns([2, 1])
    st.divider()
    with col_left:
        st.subheader("📈 Analisi Trend & Eventi Critici")
        fig_line = px.line(filtered_df, x="Year", y="GDP", color="Country Code", template="plotly_dark")
        
        # Inserimento Anomalie (Shock Economici)
        anomalies_found = filtered_df[filtered_df['Is_Anomaly'] == True]
        if not anomalies_found.empty:
            fig_line.add_trace(go.Scatter(
                x=anomalies_found['Year'], y=anomalies_found['GDP'], 
                mode='markers', marker=dict(color='#FF4B4B', size=10, symbol='x'),
                name='Shock Economico'
            ))
        fig_line.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        # Calcolo Variabili Focus
        try:
            leader_val = filtered_df.groupby('Country Code')['GDP'].last().idxmax()
        except:
            leader_val = "N/A"

        focus_data = filtered_df[filtered_df['Country Code'] == focus_country]
        if len(focus_data) > 1:
            total_growth = ((focus_data['GDP'].iloc[-1] - focus_data['GDP'].iloc[0]) / focus_data['GDP'].iloc[0]) * 100
            color_text = "#00FF00" if total_growth >= 0 else "#FF0000"
            growth_str = f"{total_growth:+.1f}%"
        else:
            growth_str = "0.0%"; color_text = "#FFFFFF"
        
        # Titolo Bianco (Stessa grandezza di Predictive Outlook)
        st.markdown(f"<h3 style='color: #FFFFFF; margin-top: 0px; font-size: 28px;'>💡 Focus & Leadership</h3>", unsafe_allow_html=True)
        st.divider()
        # Box Centralizzato con Bagliore Oro
        st.markdown(f"""
            <div style="text-align: center; background-color: #1C2128; padding: 25px; border-radius: 15px; border: 1px solid #30363D;">
                <p style="margin: 0; color: #FFFFFF; font-weight: bold; font-size: 1.1rem;">Focus {focus_country}</p>
                <h2 style="margin: 15px 0; color: #FFD700; font-size: 1.5rem; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);">{growth_str}</h2>
                <p style="margin: 0; color: #FFFFFF; font-weight: bold; font-size: 1.1rem;">Crescita nel periodo</p>
            </div>
        """, unsafe_allow_html=True)
        st.divider()
        st.markdown(f"""
            <div style="text-align: center; background-color: #1C2128; padding: 25px; border-radius: 15px; border: 1px solid #30363D;">
                <p style="margin: 0; color: #FFFFFF; font-size: 1.1rem; font-weight: bold;">Market Leader nel {to_year}</p>
                <h2 style="margin: 15px 0; color: #FFD700; font-size: 1.5rem; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);">{leader_val}</h2>
                <p style="margin: 0; color: #FFFFFF; font-weight: bold; font-size: 1.1rem;">Il PIL più elevato registrato</p>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

    # --- D. PREVISIONI (Ora in basso a tutta larghezza - Inversione Dimensioni) ---
    st.subheader("🔮 Predictive Outlook: Prossimi 5 Anni")
    fig_pred = go.Figure()
    
    for country in selected_countries:
        c_full = gdp_df[gdp_df['Country Code'] == country].dropna()
        if len(c_full) > 1:
            X = c_full['Year'].values.reshape(-1, 1)
            y = c_full['GDP'].values
            model = LinearRegression().fit(X, y)
            future = np.array(range(max_y + 1, max_y + 6)).reshape(-1, 1)
            preds = model.predict(future)
            
            fig_pred.add_trace(go.Scatter(x=c_full['Year'], y=y, name=f"{country} (Storico)"))
            fig_pred.add_trace(go.Scatter(
                x=future.flatten(), y=preds, name=f"{country} (Forecasting)", line=dict(dash='dash')
            ))
            
    fig_pred.update_layout(template="plotly_dark", height=550, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pred, use_container_width=True)
    
    st.markdown(f"""
        <div style="text-align: justify; color: #808495; font-size: 0.95rem; margin-top: 15px; border-left: 3px solid #F0BC3E; padding-left: 15px;">
            <strong>Metodologia:</strong> Regressione lineare basata sui trend 1960-{max_y}. Le proiezioni non includono shock esogeni imprevisti.
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("© 2026 RGandja | Data Intelligence Unit")