# Liste pour stocker les nouvelles lignes
new_rows = []

# Colonnes à traiter
columns_to_split = ['C', 'D', 'E', 'F', 'G', 'H']

# Parcourir chaque ligne du DataFrame
for index, row in df.iterrows():
    # Vérifier si la colonne 'AD' contient 'A'
    if row['AD'] == 'A':
        for col in columns_to_split:
            if row[col] != 0:  # Ne traiter que les valeurs non nulles
                new_row = {c: (row[c] if c == col else 0) for c in df.columns}
                new_rows.append(new_row)
    else:
        new_rows.append(row.to_dict())

# Créer un nouveau DataFrame avec les nouvelles lignes
new_df = pd.DataFrame(new_rows)

# Affichage du nouveau DataFrame
print("\nNouveau DataFrame après scission des lignes pour les colonnes sélectionnées:")
print(new_df)
