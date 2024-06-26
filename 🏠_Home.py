import pandas as pd
import streamlit as st

st.set_page_config(page_title="PAF Prévi", page_icon="🏠", layout="centered", initial_sidebar_state="auto")


st.title('Prévision flux DPAF') 


st.markdown("Onglet **Concat** : Un outil de concaténation des programmes AF Skyteam et des programmes SariaP.")
st.markdown("Onglet **Paf Prévi** : Un outil de prévisions des flux aux différents sites DPAF de l'aéroport CDG.")
st.markdown("Onglet **Vérif Seuil** : Un outil pour tracer le débit horaire des flux DPAF.")

st.sidebar.info("Version : 1.0")


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
