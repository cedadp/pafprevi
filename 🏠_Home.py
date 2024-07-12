import pandas as pd
import streamlit as st

st.set_page_config(page_title="PAF Prévis", page_icon="🛂", layout="centered", initial_sidebar_state="auto")


st.title('Prévision flux DPAF') 


st.markdown("Onglet ** 📦 Concat** : Un outil de concaténation des programmes AF Skyteam et des programmes SariaP.")
st.markdown("Onglet ** 🛂 PAF Prévis** : Un outil de prévisions des flux aux différents sites DPAF de l'aéroport CDG.")
st.markdown("Onglet ** 📊 Vérif Seuil PAF** :  Un outil de visualisation des flux horaires aux différents sites DPAF dans l'aéroport CDG.")

st.sidebar.info("Version : 1.0")


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
