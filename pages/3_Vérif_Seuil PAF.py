import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from itertools import product
import locale
from datetime import datetime, timedelta

st.set_page_config(page_title="Vérif Seuil PAF", page_icon="🛂", layout="centered", initial_sidebar_state="auto", menu_items=None)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


st.title('📊 Vérif Seuil PAF - Charge horaire ')
    
uploaded_file = st.file_uploader("Selectionner un fichier", type=["xls", "xlsx"])
    

    
if uploaded_file is not None: 
        
        df = pd.read_excel(uploaded_file)
        
# création d'un dataframe contenant toutes les combinaisons jour/heure/site
        jours= df['jour'].unique()
        heures = pd.date_range("00:00:00", "23:50:00", freq="10min").strftime('%H:%M:%S')
        sites= df['site'].unique()
    
        combinaisons = pd.DataFrame(list(product(jours,heures,sites)), columns=['jour', 'heure','site'])
       
# jointure entre le df_final et le df combinaisons pour corriger le problème d'omission de colonne lorsque charge = 0
       
        df_complet =pd.merge(df, combinaisons, on = ['jour', 'heure','site'], how = "right")
        df_complet['charge'].fillna(0, inplace=True)
                   
        df = df_complet

# afficher des calendrier pour selectionner une date de début et une date de fin d'analyse
        #st.write(jours.max() - timedelta(days=1))

        col1, col2 = st.columns(2)
        with col1:
             debut = st.date_input("Date de début :",min_value=jours.min(),max_value= jours.max() - timedelta(days=1), key=10)
        with col2:    
             fin = st.date_input("Date de fin :",value=debut,min_value=jours.min(),max_value= jours.max() - timedelta(days=1),help=" 7 jours max.", key=2) #-1 car il y a toujours quelques heures du début de la dernière journée (méthode à revoir)
    
        start_date = pd.to_datetime(debut)
        end_date = pd.to_datetime(fin)

# filtre le df sur la semaine suivante entière
        
        #jour_deb = df['jour'].min().weekday()
        #jour_a_ajouter = (7 - jour_deb) % 7
        #deb_semaine_deux= df['jour'].min() + pd.Timedelta(days=jour_a_ajouter)
        
        #fin_semaine_deux = deb_semaine_deux+ pd.Timedelta(days=6)
        
        
        df['jour']= pd.to_datetime(df['jour'])
        df = df[(df['jour'] >= start_date)&(df['jour']<= end_date)]
        
        
        if st.button('Tracer flux PAF'):    

             
            df = df.sort_values(by=['site', 'jour', 'heure'])
    
    #transforme le dataframe dans un format "large"        
            
            df_pivot = df.pivot (index=['site', 'jour'], columns='heure', values='charge').reset_index() 
            
            
    # calcul du cumul de charge horaire glissant à partir de données 10 min
            
            def calculate_sums(row): 
                sums = {}
                times = df_pivot.columns[2:]
                for i in range(len(times)-5):
                    sum_value=sum(row[times[j]] for j in range (i,i+6))
                    sums[times[i+5]] = sum_value
                return pd.Series(sums)
            
            new_df = df_pivot.apply (calculate_sums, axis=1)
                
            new_df.insert(0, 'site', df_pivot['site'])
            new_df.insert(1, 'jour', df_pivot['jour'])        
        
        # retourne le dataframe dans un format "long"
        
            df_depivote = pd.melt(new_df, id_vars=['site', 'jour'], var_name='heure', value_name='charge')
    
             
                                      
    #new_df.to_excel("C:/Users/demanet/Downloads/test_cumul.xlsx", index= False)        
            
      
            
    #créer une liste dynamique des sites (revient à faire unique(), mais permet ici de supprmier les sites fermées)
            df_config =df.groupby(['site'], as_index=False)['charge'].sum()
            df_config =df_config[df_config['charge'] > 0]
            df_config = df_config.drop(columns=['charge'])
            
                      
            #custom_dict = {'K CTRCNT' : 0,'K CTR' : 1,'K CNT' : 2 , 'L CTR' : 3, 'L CNT' : 4, 'M CTR' : 5, 'Galerie EF' : 6, 'C2F' : 7, 'C2G' : 8, 'Liaison AC' : 9,'Liaison BD' : 10,
            #'T3': 11, 'Terminal 1' : 12, 'Terminal 1_5' : 13, 'Terminal 1_6' : 14}
            
            custom_dict = {'2E_Arr':0,'2E_Dep':1,'S3 > F':2,'F > S3':3,'Galerie E > F':4,'Galerie F > E':5,'BD_Arr':6,'BD_Dep':7,'T1_Arr':8,'T1_Dep':9,'T3_Arr':10,'T3_Dep':11,'AC_Arr':12,'AC_Dep':13}

            
            
            df_config = df_config.sort_values(by=['site'], key=lambda x: x.map(custom_dict)).reset_index(drop=True)
        
            
            
            
            
            
            sites = df_config['site'].unique() # permet de créer un tableau simple à partir du dataframe df_complet (à revoir)
            
            
        # seuils de saturation    
            
            
            def seuil(site):
                #seuils = {'K CTRCNT' : 0,'K CTR' : 1600,'K CNT' : 300 , 'L CTR' : 2100, 'L CNT' :  1440, 'M CTR' : 1820, 'Galerie EF' : 1820, 'C2F' : 2180, 'C2G' : 910, 'Liaison AC' : 1960,'Liaison BD' : 2500,
                #'T3': 1260, 'Terminal 1' : 2280, 'Terminal 1_5' : 375, 'Terminal 1_6' : 500}
                seuils = {'2E_Arr':3600,'2E_Dep':3966,'S3 > F':968,'F > S3':2222,'Galerie E > F':2744,'Galerie F > E':1240,'BD_Arr':2276,'BD_Dep':1544,'T1_Arr':2664,'T1_Dep':2071,'T3_Arr':1180,'T3_Dep':1020,'AC_Arr':1780,'AC_Dep':1248}
            
                return seuils.get(site,0)
            
        
        # graphique   
        
            for site in sites: 
                
                st.subheader(f" {site}")
                
                st.write("seuil max: ", seuil(site))
                df_site = df_depivote.loc[df_depivote['site']==site]
                locale.setlocale(locale.LC_ALL, 'fr_FR')
                df_site['Date']= df_site['jour'].dt.strftime('%A %d %b')
               
                fig = px.line(df_site, x= 'heure', y= 'charge',  color = 'Date',
                                labels={'jour', 'date'})
                
                ligne_seuil = seuil(site)
                fig.add_hline(y=ligne_seuil, line_dash='dash', line_color="red")
                
                
                
                st.plotly_chart(fig)
