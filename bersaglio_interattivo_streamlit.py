import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import os

st.title("🎯 Allenamento tiro con l’arco – Inserimento frecce")

# === Parametri sessione ===
distanza = st.text_input("Inserisci la distanza di tiro (es. 18m, 30m):", "18m")
frecce_per_volee = st.selectbox("Quante frecce per volee?", [3, 6])

now = datetime.now()
session_id = now.strftime('%Y-%m-%d_%H-%M')
timestamp = now.strftime('%Y-%m-%d %H:%M')
storico_file = "storico_frecce.csv"

# === Stato persistente ===
if "tiri" not in st.session_state:
    st.session_state.tiri = []
if "volee_numero" not in st.session_state:
    st.session_state.volee_numero = 1
if "volee_corrente" not in st.session_state:
    st.session_state.volee_corrente = []

def calcola_punteggio(x, y):
    d = np.sqrt(x**2 + y**2)
    if d <= 1: return 10
    elif d <= 2: return 9
    elif d <= 3: return 8
    elif d <= 4: return 7
    elif d <= 5: return 6
    elif d <= 6: return 5
    elif d <= 7: return 4
    elif d <= 8: return 3
    elif d <= 9: return 2
    elif d <= 10: return 1
    else: return 0

def disegna_bersaglio(tiri):
    fig, ax = plt.subplots(figsize=(6, 6))
    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for i in range(5):
        for _ in range(2):
            ax.add_patch(patches.Circle((0,0), r, color=colori[i], ec="black"))
            r -= 1

    for x,y,p,v in tiri:
        ax.plot(x, y, marker="x", color="limegreen", markersize=6)

    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig

st.subheader(f"Volee {st.session_state.volee_numero}")
with st.form("inserisci_freccia"):
    x = st.number_input("X", -10.0, 10.0, 0.0, 0.1)
    y = st.number_input("Y", -10.0, 10.0, 0.0, 0.1)
    aggiungi = st.form_submit_button("➕ Aggiungi freccia")

if aggiungi:
    p = calcola_punteggio(x,y)
    st.session_state.volee_corrente.append((x,y,p))
    st.session_state.tiri.append((x,y,p, st.session_state.volee_numero))
    st.success(f"Freccia registrata: ({x:.2f}, {y:.2f}) → {p} punti")

    if len(st.session_state.volee_corrente) >= frecce_per_volee:
        st.info(f"✅ Volee {st.session_state.volee_numero} completata")
        st.session_state.volee_numero += 1
        st.session_state.volee_corrente = []

# Mostra bersaglio
if st.session_state.tiri:
    st.pyplot(disegna_bersaglio(st.session_state.tiri))

# Fine sessione
if st.button("🏁 Termina allenamento e salva"):
    df = pd.DataFrame(st.session_state.tiri, columns=["x","y","punteggio","volee"])
    df["distanza"] = distanza
    df["session_id"] = session_id
    df["datetime"] = timestamp
    df["freccia"] = df.groupby("volee").cumcount() + 1

    if os.path.exists(storico_file):
        df_old = pd.read_csv(storico_file)
        df_all = pd.concat([df_old, df], ignore_index=True)
    else:
        df_all = df

    df_all.to_csv(storico_file, index=False)
    st.success("✅ Sessione salvata nello storico!")
