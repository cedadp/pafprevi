import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Titre de l'application
st.title("Analyse des Écarts entre Trajets Réalisés et Prévisionnels")

# Importation des fichiers via l'interface
uploaded_file_realise = st.file_uploader("Upload le fichier de trajets réalisés (Excel)", type=["xlsx"])
uploaded_file_previsionnel = st.file_uploader("Upload le fichier de trajets prévisionnels (CSV)", type=["csv"])

if uploaded_file_realise is not None and uploaded_file_previsionnel is not None:
    # Charger les fichiers
    df_realises = pd.read_excel(uploaded_file_realise)
    df_previsionnels = pd.read_csv(uploaded_file_previsionnel)

    # Concaténer code compagnie et numéro de trajet pour le fichier prévisionnel
    df_previsionnels['numero_trajet'] = df_previsionnels['code compagnie'].astype(str) + '-' + df_previsionnels['numéro de trajet'].astype(str)

    # Renommer la colonne numéro de trajet du fichier réalisé
    df_realises.rename(columns={'numéro de trajet': 'numero_trajet'}, inplace=True)

    # Fusionner les deux DataFrames sur le numéro de trajet et le jour
    df_comparaison = pd.merge(df_realises, df_previsionnels, how='inner', left_on=['numero_trajet', 'jour'], right_on=['numero_trajet', 'date'])

    # Calculer l'écart de passagers entre prévu et réalisé
    df_comparaison['ecart_passagers'] = df_comparaison['nombre de passagers_x'] - df_comparaison['nombre de passagers_y']

    # Afficher les résultats dans Streamlit
    st.subheader("Résultats de la Comparaison")
    st.write(df_comparaison[['numero_trajet', 'jour', 'code compagnie_x', 'nombre de passagers_x', 'nombre de passagers_y', 'ecart_passagers']])

    # Visualisation de la distribution des écarts
    st.subheader("Distribution des Écarts entre Passagers Réalisés et Prévisionnels")

    plt.figure(figsize=(10,6))
    sns.histplot(df_comparaison['ecart_passagers'], kde=True, color='blue', bins=20)
    plt.title("Distribution des Écarts de Passagers")
    plt.xlabel("Écart de Passagers")
    plt.ylabel("Fréquence")
    st.pyplot(plt)

    # Visualisation des boîtes à moustaches par compagnie
    st.subheader("Boîtes à Moustaches des Écarts par Compagnie")

    plt.figure(figsize=(12,6))
    sns.boxplot(x='code compagnie_x', y='ecart_passagers', data=df_comparaison)
    plt.title("Dispersion des Écarts par Compagnie")
    plt.xlabel("Compagnie")
    plt.ylabel("Écart de Passagers")
    st.pyplot(plt)
