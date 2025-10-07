import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import os

st.title("📊 Dashboard storico frecce")

storico_file = "storico_frecce.csv"
if not os.path.exists(storico_file):
    st.error("⚠️ Nessun file storico trovato. Fai prima una sessione.")
    st.stop()

df = pd.read_csv(storico_file)
df['datetime'] = pd.to_datetime(df['datetime'])
df['distanza'] = df['distanza'].astype(str).str.strip()

intervalli = {
    "Ultimi 7 giorni": 7,
    "Ultimi 15 giorni": 15,
    "Ultimo mese": 30,
    "Ultimi 3 mesi": 90,
    "Ultimo anno": 365,
    "Tutto": None
}

distanza = st.selectbox("Distanza:", sorted(df['distanza'].unique()))
tipo = st.radio("Filtro per:", ["Intervallo di tempo", "Sessione"])

if tipo == "Intervallo di tempo":
    valore = st.selectbox("Periodo:", list(intervalli.keys()))
    oggi = datetime.now()
    if intervalli[valore]:
        start = oggi - timedelta(days=intervalli[valore])
    else:
        start = df['datetime'].min()
    df_filtrato = df[(df['distanza']==distanza) & (df['datetime'] >= start)]
else:
    sessioni = sorted(df[df['distanza']==distanza]['session_id'].unique())
    valore = st.selectbox("Sessione:", sessioni)
    df_filtrato = df[(df['distanza']==distanza) & (df['session_id']==valore)]

# Disegna bersaglio
def disegna_bersaglio(data):
    fig, ax = plt.subplots(figsize=(6,6))
    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for i in range(5):
        for _ in range(2):
            ax.add_patch(patches.Circle((0,0), r, color=colori[i], ec="black"))
            r -= 1
    for _,row in data.iterrows():
        ax.plot(row['x'], row['y'], marker="x", color="limegreen", markersize=6)
    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig

if df_filtrato.empty:
    st.warning("Nessuna freccia trovata per i criteri selezionati.")
else:
    st.pyplot(disegna_bersaglio(df_filtrato))

    media_punteggio = df_filtrato['punteggio'].mean()
    centro_x = df_filtrato['x'].mean()
    centro_y = df_filtrato['y'].mean()
    distanza_media = (df_filtrato['x']**2 + df_filtrato['y']**2).pow(0.5).mean()
    dev_standard = (df_filtrato['x']**2 + df_filtrato['y']**2).pow(0.5).std()

    st.markdown(f"""
    **🎯 Frecce:** {len(df_filtrato)}  
    **📊 Totale:** {df_filtrato['punteggio'].sum()} | **Medio:** {media_punteggio:.2f}  
    **📍 Centro medio:** ({centro_x:.2f}, {centro_y:.2f})  
    **📏 Distanza media:** {distanza_media:.2f}  
    **📉 Dev. standard:** {dev_standard:.2f}  
    """)

