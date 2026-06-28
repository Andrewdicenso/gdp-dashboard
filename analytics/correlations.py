import streamlit as st
import plotly.express as px

def render_correlation_analysis(df, focus_paese, paesi_selezionati):
    
    st.markdown("### 🔗 Analisi delle Correlazioni Strategiche")
    
    if focus_paese in df.columns and len(paesi_selezionati) > 1:
        # Calcolo logico
        corr_matrix = df[paesi_selezionati].corr()
        focus_corr = corr_matrix[focus_paese].drop(focus_paese).sort_values(ascending=False)
        
        # Visualizzazione
        fig = px.bar(focus_corr, orientation='h', 
                     title=f"Correlazione tra {focus_paese} e altri mercati",
                     labels={'value': 'Indice di Correlazione', 'index': 'Paese'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aggiungi più paesi nei filtri per vedere le correlazioni.")