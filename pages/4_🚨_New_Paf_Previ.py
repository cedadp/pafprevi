import pandas as pd  
import streamlit as st
import numpy as np
import datetime
from functools import reduce
import time as tm
import openpyxl
   
st.set_page_config(page_title="Paf Previ", page_icon="🚨", layout="centered", initial_sidebar_state="auto", menu_items=None)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.title("PreviPAF")
st.subheader("Programme complet :")
uploaded_file = st.file_uploader("Choisir un fichier :", key=1)
if uploaded_file is not None:
    @st.cache(suppress_st_warning=True,allow_output_mutation=True)
    def df():
        with st.spinner('Chargemement Programme complet ...'):
            df = pd.read_excel(uploaded_file, "pgrm_complet")
            df['Libellé terminal'] = df['Libellé terminal'].str.replace("T1_Inter","Terminal 1")
            df['Libellé terminal'] = df['Libellé terminal'].str.replace("T1_5","Terminal 1_5")
            df['Libellé terminal'] = df['Libellé terminal'].str.replace("T1_6","Terminal 1_6")
        st.success("Programme complet chargée !")
        return df

    df_pgrm = df()         
    start_all = tm.time()
    l_date = pd.to_datetime(df_pgrm['Local Date'].unique().tolist()).date
    l_date = sorted(l_date)
    uploaded_file1 = st.file_uploader("Choisir le fichier hypotheses_repartition_correspondances.xlsx :", key=4)
    if uploaded_file1 is not None:
        @st.cache(suppress_st_warning=True,allow_output_mutation=True)
        def HYPOTHESE_REP():
            df = pd.read_excel(uploaded_file1, name_hyp, engine='openpyxl')
            df['plage'] = 'am'
            df.loc[df['heure_debut']>=(datetime.time(17)) , 'plage'] = 'pm'             
            return df
    @st.cache(suppress_st_warning=True,allow_output_mutation=True)
    def COURBE_PRES(t):
        df = pd.read_excel('courbes_presentation.xlsx', t)
        return df      
    col1, col2 = st.columns(2)
    with col1:
        debut = st.date_input("Date de début :", key=10)
    with col2:    
        fin = st.date_input("Date de fin :", key=2)
    
    start_date = pd.to_datetime(debut)
    end_date = pd.to_datetime(fin) 

    if st.button('Créer Export PAF'):
    


        #Fonction qui regroupe les sous fonctions de traitement


        
        st.warning('La requête a bien été prise en compte, début du traitement.\nNe tentez pas de fermer la fenêtre même si celle-ci semble figée')
    ### path files ###
        path_hyp = r"" + "hypotheses_repartition_correspondances.xlsx"
        name_hyp = "Feuil1"
        
        path_faisceaux = r"" + "faisceaux_escales.xlsx"
        name_faisceaux = "escales"
        
    #        ancienne courbes de prés globale, sans distinction de terminal
    #        path_courbes = r"" + source_outils_previ.chemin_fichier_source(4)
    #        name_courbes = "nouvellesCourbesPresentation"
        
        path_courbes_term = r"" + "nouvelles_courbes_presentation_PIF.xlsx"
        list_terminaux = ['T2AC', 'T2BD', 'T2E', 'T2F', 'T2G', 'T3','T1_Inter','T1_5','T1_6']
        
        list_terminaux_P4 = ['Terminal 2A', 'Terminal 2B', 'Terminal 2C', 'Terminal 2D',
                           'Terminal 3','Terminal 1',
                          'Terminal 1_5','Terminal 1_6']

        path_output = r"" + "output_export_paf"
        name_output = "export_paf"
        


        
        def FAISCEAUX_IATA():
            df = pd.read_excel(path_faisceaux, name_faisceaux)
            del df['faisceau_facturation']
            del df['faisceau_commercial']
            del df['cl_long']
            del df['pays']
            del df['ville']
            del df['aeroport']
            del df['escale_OACI']
            del df['jour_ref']
            del df['statut']
            return df
        
        df_faisceaux = FAISCEAUX_IATA()
        
        
    #        Pour la courbe de pres unique, inutile
    #        def COURBE_PRESENTATION():
    #            return pd.read_excel(path_courbes, name_courbes)
        
    #        df_courbe_presentation = COURBE_PRESENTATION()
        df_hyp_rep = HYPOTHESE_REP()
        
        
    #        Entre pgrm ADP et pgrm AF les heures ne sont pas au même format. On les transforme ici. A terme migrer cette fonction dans Concat
        def STR_TO_DT(df):
            df_temp = df
            l_dt = []
            for t in range(df.shape[0]):
                TSTR =  str(df['Horaire théorique'][t])
                if len(TSTR)<10:
                    l = [int(i) for i in TSTR.split(':')]
                    l_dt.append(datetime.time(hour=l[0], minute=l[1], second=0))
                else:
                    TSTR = TSTR[10:]
                    l = [int(i) for i in TSTR.split(':')]
                    l_dt.append(datetime.time(hour=l[0], minute=l[1], second=0))
            
            df['Horaire théorique'] = l_dt
                
            return df_temp
        
        df_pgrm_dt = STR_TO_DT(df_pgrm)
        df_pgrm_dt = df_pgrm_dt.loc[(df_pgrm_dt['Local Date'] >= start_date) & (df_pgrm_dt['Local Date'] <= end_date)]
        df_pgrm_dt.reset_index(inplace=True, drop=True)
        df_pgrm_dt['Unnamed: 0'] = df_pgrm_dt.index
        

        

        
    ### DISPATCH ###   
        import numpy
        from datetime import datetime, timedelta    
        def DISPATCH_NEW(df, hyp_rep):
            """Permet la création d'un DF dispatch qui facilite le tri par batterie de PAF"""
            col = ['Local Date', 'Horaire théorique', 'Prov Dest', 'A/D', 'Libellé terminal','L CTR']

            #                IMPLEMENTATION T1

            dispatch_df = pd.DataFrame(columns = col, index = df['Unnamed: 0'])
            st.write(df)
            dispatch_df['Local Date'] = df['Local Date']
            dispatch_df['Horaire théorique'] = df['Horaire théorique']
            dispatch_df['Prov Dest'] = df['Prov Dest']
            dispatch_df['A/D'] = df['A/D']
            dispatch_df['Libellé terminal'] = df['Libellé terminal']
            #dispatch_df['faisceau_geographique'] = df['faisceau_geographique']

        #           variable 1ere ligne a lire : "hypothèse de répartition K vers terminal2ABCD le matin (am = matin, pm = soir cad après 17h)

        #            Si une erreur de flottant survient, cela provient certainement d'ici : les valeurs ne sont pas considérées comme des flottants mais en série d'un element 
        #            donc on les transforme en liste puis on récupère le 1er (et normalement unique élément). Contrairement aux 6 d'avant qui eux sont directement des flottants 
        #           grace au "1 - valeur"
        #            En cas de bug Retirez le .tolist()[0] 
            def hyp_rep_salle(salle_apport, salle_emport, periode):
                return hyp_rep.loc[(hyp_rep['salle_apport'] == salle_apport) & (hyp_rep['salle_emport'] == salle_emport) & (hyp_rep['heure_debut'] == hyp_rep[periode][0])]['taux'].tolist()[0]
                

            def dispatch_term(AD, terminal, periode, type_pax = 'Pax CNT TOT', _terminal2 = None):
                if _terminal2 == None:
                    temp = df.loc[(df['A/D'] == AD) & (df['Libellé terminal'] == terminal)]
                else:
                    temp = df.loc[(df['Libellé terminal'] == terminal) | (df['Libellé terminal'] == _terminal2)]
                    temp = temp.loc[temp['A/D'] == AD] #erreur mettre "AD" à la place de periode (à vérifier)
                    
                if periode == 'am':
                    return temp.loc[(temp['Horaire théorique'] >= hyp_rep['heure_debut'][0]) & (temp['Horaire théorique'] < hyp_rep['heure_fin'][0])][type_pax]
                elif periode == 'pm' :
                    return temp.loc[(temp['Horaire théorique'] >= hyp_rep['heure_fin'][0])][type_pax]
                else:
                    return "erreur periode"


        #            Dans chaque colonne de dispatch on a les batteries de PIF, 
        #           et comme on a filtré les vols de la logique des PIF dans l_a_k_am par exemple 
        #           on le multiplie par la proportion de gens allant de K vers T2ABDC (ces PAX utilisent le K CNT), ainsi de suite pour chaque PIF
        #           
        #           Reduce permet ici d'additionner les sous dataframe ensembles et de combler les nan par 0. L'index est tjr celui de df_pgrm_dt, ligne de vol à vol

        #    L CTR
            dispatch_df['L CTR'] = reduce(lambda a, b: a.add(b, fill_value = 0), 
                        [dispatch_term('A', "EK", "am") * hyp_rep_salle('salle K', 'salle L', 'heure_debut'),
                        dispatch_term('A', "EK", "pm") * hyp_rep_salle('salle K', 'salle L', 'heure_fin'),
                        dispatch_term('D', "EL", "am", 'Pax LOC TOT'), 
                        dispatch_term('D', "EL", "pm", 'Pax LOC TOT'),
                        dispatch_term('A', "EM", "am") * hyp_rep_salle('salle M', 'salle L', 'heure_debut'), 
                        dispatch_term('A', "EM", "pm") * hyp_rep_salle('salle M', 'salle L', 'heure_fin')])

            st.write(dispatch_df['L CTR'].sum())
                        
            dispatch_df.fillna(0, inplace=True)

            return dispatch_df

 
        dispatch = DISPATCH_NEW(df_pgrm_dt, df_hyp_rep)
        

        liste_df_courbe_presentation_terminal = {}
        
        for t in list_terminaux:
            liste_df_courbe_presentation_terminal[t] = COURBE_PRES(t)
        
        def courbe(df_c):
            l_f = df_c['faisceau_geographique'].unique().tolist()
            
            courbe = {}
            for i in l_f:    
                courbe[i] = ( df_c['pourc'].loc[(df_c['faisceau_geographique'] == i)
                                                & (df_c['heure_debut'] == df_c['heure_debut'][0])].tolist())
            return courbe

        l_courbe_geo_t = {}

        for t in list_terminaux:    
            l_courbe_geo_t[t] = courbe(liste_df_courbe_presentation_terminal[t])

        st.write(l_courbe_geo_t)

        l_faisceaux = [i for i in l_courbe_geo_t['T2E'].keys()]
        
        from scipy import signal 
            
        def CREATE_DF_SITE(dispatch_df, site):
            """Permet de créer le format de l'export paf final"""
            c = ['jour', 'heure', 'site', 'charge', 'type']
            l_pas10min = pd.date_range(pd.datetime(2022,1,1), periods=144, freq="10T").time.tolist()
            df = pd.DataFrame(columns=c)
            l_jour = dispatch_df['Local Date'].sort_values(ascending = True).unique().tolist()
            nb_jour = len(l_jour)
            df['heure'] = l_pas10min * nb_jour
            df['site'] = site
            df['charge'] = 0
            df['type'] = "pafbi_python"
            for i in range(len(l_jour)):
                df.iloc[144*i:144*(i+1), 0] = pd.to_datetime(l_jour[i])
            return df
        
        def ITERATE_SITE(dispatch_df):
            l_df_site = {}
            l_site = dispatch_df.columns.tolist()
            for site_i in range(5, dispatch_df.shape[1]):
                l_df_site[l_site[site_i]] = CREATE_DF_SITE(dispatch_df, l_site[site_i])
                
            return l_df_site
        

        st.write(dispatch)

        dispatch_paf = dispatch.copy()

        dispatch_paf_D = dispatch_paf.copy()
        dispatch_paf_D = dispatch_paf_D[dispatch_paf_D["A/D"] == "D"]

        st.write(dispatch_paf_D)
        courbe_deb_l = [0.33, 0.33, 0.33]
        convo = list(signal.convolve(dispatch_paf_D["L CTR"], courbe_deb_l, mode='same'))
        st.write(convo)
        
        l_courbe_geo_t = {}
        
        for t in list_terminaux:
            df_courbe = COURBE_PRES(t).copy()
            l_courbe_geo_t[t] = {}
            for i in df_courbe["faisceau_geographique"].unique():
                temp = df_courbe.copy()
                temp = temp[temp["faisceau_geographique"].copy()==i].copy()
                l_courbe_geo_t[t][i] = {}
                for j in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P0"]:
                    l_courbe_geo_t[t][i][j] = {}
                    # st.write(df_courbe)
                    # st.write(t)
                    # st.write(l_courbe_geo_t[t][i][j])
                    l_courbe_geo_t[t][i][j] = temp[j].tolist()
                    



        dispatch_paf = dispatch.copy()



        dispatch_paf['new_date'] = dispatch_paf['Local Date'].dt.date
        dispatch_paf['new_time'] = dispatch_paf['Horaire théorique'].dt.time
        dispatch_paf['new_datetime'] = pd.to_datetime(dispatch_paf['new_date'].astype(str) + ' ' + dispatch_paf['new_time'].astype(str))

        dispatch_paf.loc[(dispatch_paf['Libellé terminal'].isin(list_terminaux_P4)) & (dispatch_paf['Horaire théorique']>datetime(1900, 1, 1, 0, 00, 00, 0)), 'Plage'] = 'P2'
        dispatch_paf.loc[(dispatch_paf['Libellé terminal'].isin(list_terminaux_P4)) & (dispatch_paf['Horaire théorique']>datetime(1900, 1, 1, 11, 00, 00, 0)), 'Plage'] = 'P4'
        dispatch_paf.loc[(dispatch_paf['Libellé terminal'].isin(list_terminaux_P4)) & (dispatch_paf['Horaire théorique']>datetime(1900, 1, 1, 15, 00, 00, 0)), 'Plage'] = 'P5'
        dispatch_paf.loc[(dispatch_paf['Libellé terminal'].isin(list_terminaux_P4)) & (dispatch_paf['Horaire théorique']>datetime(1900, 1, 1, 17, 00, 00, 0)), 'Plage'] = 'P6'
        dispatch_paf.loc[(dispatch_paf['Libellé terminal'].isin(list_terminaux_P4)) & (dispatch_paf['Horaire théorique']>datetime(1900, 1, 1, 19, 00, 00, 0)), 'Plage'] = 'P7'



        dispatch_paf_D = dispatch_paf.copy()
        dispatch_paf_D = dispatch_paf_D[dispatch_paf_D["A/D"] == "D"]
        dispatch_paf_A = dispatch_paf.copy()
        dispatch_paf_A = dispatch_paf_A[dispatch_paf_A["A/D"] == "A"]


        n_D = 24
        n_A = 4 #len(L_A)

        # Create a list to store the duplicated rows
        rows = []
        L_A = [0, 0, 0.5, 0.5]
        L_pif = ['K CNT', 'K CTR', 
                    'L CNT', 'L CTR', 
                    'M CTR', 
                    'Galerie EF', 'C2F', 
                    'C2G', 
                    'Liaison AC', 
                    'Liaison BD', 
                    'T3',
                    'Terminal 1',
                    'Terminal 1_5',
                    'Terminal 1_6']



        # st.write(dispatch_paf_D)
        # dispatch_paf_D['Libellé terminal'].replace({"F":"C2F",
        #                                             "G":"C2G",
        #                                             "EM":"M CTR",
        #                                             "EL":"L CTR",
        #                                             "EK":"K CTR",},
        #                                               inplace=True)
        
        
        # DEPART
        # Loop through each row in the dataframe
        for index, row in dispatch_paf_D.iterrows():
            # Loop n times to duplicate the row and subtract 10 minutes from the datetime column each time
            for i in range(n_D):
                # Create a copy of the original row
                new_row = row.copy()
                if new_row['Faisceau géographique'] == 0:
                    x = "Extrême Orient"
                else:
                    x = new_row['Faisceau géographique']    
                L = l_courbe_geo_t[new_row['Libellé terminal']][x][new_row['Plage']]               
                # Subtract 10 minutes from the datetime column
                new_row['new_datetime'] -= timedelta(minutes=10*i)
                for pif in L_pif:
                    new_row[pif] = L[i]*new_row[pif]
                
                # Append the modified row to the list
                rows.append(new_row)
                
                
        # Create a new dataframe from the list of duplicated rows
        new_df = pd.DataFrame(rows)


        # ARRIVER

        for index, row1 in dispatch_paf_A.iterrows():
            # Loop n times to duplicate the row and subtract 10 minutes from the datetime column each time
            for i in range(n_A):
                # Create a copy of the original row
                new_row = row1.copy()
                # Subtract 10 minutes from the datetime column
                new_row['new_datetime'] += timedelta(minutes=10*i)
                for pif in L_pif:
                    new_row[pif] = L_A[i]*new_row[pif]
                
                # Append the modified row to the list
                rows.append(new_row)
                
                
        # Create a new dataframe from the list of duplicated rows
        new_df_A = pd.DataFrame(rows)

        

        new_df_A['Local Date'] = new_df_A['new_datetime'].dt.date
        new_df_A['Horaire théorique'] = new_df_A['new_datetime'].dt.time

        df_final = pd.melt(new_df_A, id_vars=['new_datetime'], value_vars=L_pif)

        def ceil_dt(x):
            return x + (datetime.min - x) % timedelta(minutes=10)

        df_final['new_datetime'] = df_final['new_datetime'].apply(lambda x: ceil_dt(x))        
        df_final['Horaire théorique'] = df_final['new_datetime'].dt.time
        df_final['new_datetime'] = df_final['new_datetime'].dt.date

        df_final = df_final.groupby(['new_datetime', 'Horaire théorique', 'variable']).sum().reset_index()
        
        df_final.rename(columns={"new_datetime":"jour",
                         'Horaire théorique':'heure',
                         'variable':'site',
                         'value':'charge'}, inplace=True)


        import time
        def CLEAN_TIME(m):
            t = '0:00'.join(str(m).rsplit('5:00', 1))
            #l = [int(k) for k in t.split(':')]
            time_r = time(hour = int(t[11:13]), minute = int(t[14:16]), second = int(t[17:19]))

            return time_r
        
        directory_exp = "export_paf_du_" + str(start_date.date()) + "_au_" + str(end_date.date()) + ".xlsx"
        from io import BytesIO  
        from pyxlsb import open_workbook as open_xlsb

        def download_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=name_output, index=False)
            writer.close()
            processed_data = output.getvalue()
            return processed_data
        
        
        

        processed_data = download_excel(df_final)
        st.download_button(
        label="Télécharger fichier Export pif",
        data=processed_data,
        file_name=directory_exp,
        mime="application/vnd.ms-excel"
        )

