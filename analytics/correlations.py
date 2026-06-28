import streamlit as st
import plotly.express as px
import pandas as pd

def render_correlation_analysis(df, focus_country, selected_countries):
    if len(selected_countries) < 2:
        st.info("Seleziona almeno due paesi per confrontare le correlazioni.")
        return

    # Prepariamo i dati: Anno come indice, Paesi come colonne
    pivot_df = df[df['Country Code'].isin(selected_countries)].pivot(
        index='Year', columns='Country Code', values='GDP'
    ).dropna()

    if focus_country in pivot_df.columns:
        # Calcolo correlazione
        corrs = pivot_df.corr()[focus_country].drop(focus_country).sort_values(ascending=False)
        
        fig = px.bar(
            corrs, 
            orientation='h',
            title=f"Sinergia Economica con {focus_country}",
            labels={'value': 'Indice di Correlazione (0-1)', 'Country Code': 'Paese'},
            color=corrs,
            color_continuous_scale='Sunset'
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"**Insight:** Una correlazione alta indica che l'economia di {focus_country} tende a muoversi in sincrono con quella del paese partner.")