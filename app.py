from flask import Flask, jsonify, request, redirect, url_for, render_template, flash, session
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Clé secrète pour les sessions

# Dictionnaire pour stocker les utilisateurs (remplacer par une base de données en production)
users = {
    "lass": "lass",
    "user2": "password2"
}

#Quelques fonctions du modèle 1

# Définir un modèle simulé basé sur les données d'origine (Si le modèle n'existe pas encore)
class ClientModel:
    def __init__(self, df):
        self.df = df
        # Encodage des variables catégorielles
        self.le_zone = LabelEncoder()
        self.le_frequence_recharge = LabelEncoder()
        self.le_canal_recharge = LabelEncoder()

        # S'assurer que les colonnes sont bien présentes
        if 'Zone' in self.df.columns:
            self.df['Zone_encoded'] = self.le_zone.fit_transform(self.df['Zone'])
        if 'Frequence_recharge' in self.df.columns:
            self.df['Frequence_recharge_encoded'] = self.le_frequence_recharge.fit_transform(self.df['Frequence_recharge'])
        if 'Canal_recharge' in self.df.columns:
            self.df['Canal_recharge_encoded'] = self.le_canal_recharge.fit_transform(self.df['Canal_recharge'])

        # Calcul de la similarité cosinus
        self.df_encoded = self.df[['Zone_encoded', 'Frequence_recharge_encoded', 'Canal_recharge_encoded']]
        self.cosine_similarities = cosine_similarity(self.df_encoded)

        # Dictionnaire des informations clients
        self.client_info_dict = self.df.set_index('MDN')[[
            'Zone', 'Frequence_recharge', 'Endroit_recharge', 'Canal_recharge', 'Nom_et_prenom'
        ]].to_dict(orient='index')

    def get_client_info(self, mdn):
        """Retourner les informations d'un client basé sur son MDN"""
        mdn = str(mdn).strip()  # Assurez-vous que le MDN est une chaîne propre
        info = self.client_info_dict.get(mdn)
        if info:
            return info
        else:
            return {
                "Zone": None,
                "Frequence_recharge": None,
                "Endroit_recharge": None,
                "Canal_recharge": None,
                "Nom_et_prenom": None
            }

    def recommander_clients_similaires(self, client_id, top_n=5):
        """Recommander les clients similaires basés sur la similarité cosinus"""
        similarity_scores = self.cosine_similarities[client_id]
        similar_clients = similarity_scores.argsort()[::-1]
        recommended_clients = self.df.iloc[similar_clients[1:top_n+1]][['MDN', 'Zone', 'Frequence_recharge', 'Canal_recharge']]
        return recommended_clients.to_dict(orient='records')

    def get_frequent_recharge_frequency(self, zone):
        """Retourner la fréquence de recharge la plus fréquente pour une zone"""
        frequence_recharge_par_zone = self.df.groupby('Zone')['Frequence_recharge'].agg(lambda x: x.mode()[0])
        return frequence_recharge_par_zone.get(zone, "Zone non trouvée dans les données.")

    def get_most_used_channel(self, zone):
        """Retourner le canal de recharge le plus utilisé pour une zone"""
        canal_recharge_par_zone = self.df.groupby('Zone')['Canal_recharge'].agg(lambda x: x.mode()[0])
        return canal_recharge_par_zone.get(zone, "Zone non trouvée dans les données.")

# Charger les données depuis un fichier CSV
df = pd.read_csv(r"D:\A_INGC\Mémoire_Rapport\Mémoire\Mémoire_Ibrahim\projets_API_sondage\df.csv", delimiter=";")
# Nettoyer les noms des zones (retirer espaces superflus et unifier les majuscules)
df['Zone'] = df['Zone'].str.strip().str.upper()
df['MDN'] = df['MDN'].astype(str).str.strip()  # Nettoyez les MDN
# Corriger les erreurs connues
corrections = {
    "ZIGUNICNHOR": "ZIGUINCHOR"
}

df['Zone'] = df['Zone'].replace(corrections)

# Nettoyer les noms des colonnes (retirer les espaces ou caractères invisibles)
df.columns = df.columns.str.strip()

# Vérifier si la colonne 'Cluster' existe et ajouter une colonne par défaut si elle est absente
if 'Cluster' not in df.columns:
    print("Avertissement: La colonne 'Cluster' est absente du DataFrame.")
    # Encodage des variables catégorielles
    le_zone = LabelEncoder()
    le_difficulte_recharge = LabelEncoder()
    le_jugement_service = LabelEncoder()

    df['Zone_encoded'] = le_zone.fit_transform(df['Zone'])
    df['Difficulte_recharge_encoded'] = le_difficulte_recharge.fit_transform(df['Difficulte_recharge'])
    df['Jugement_service_encoded'] = le_jugement_service.fit_transform(df['Jugement_service'])

    # Création d'un DataFrame encodé pour le clustering
    df_cluster = df[['Zone_encoded', 'Difficulte_recharge_encoded', 'Jugement_service_encoded']]

    # Définir le nombre de clusters (par exemple, 5 clusters)
    kmeans = KMeans(n_clusters=5, random_state=0)
    df['Cluster'] = kmeans.fit_predict(df_cluster)

#chargement des modèles

try:
    model1 = pickle.load(open('modele_1.pkl', 'rb'))
except Exception as e:
    print("Erreur lors du chargement du modèle :", e)
    model1 = None

model2 = pickle.load(open('modele_complet_2.pkl', 'rb'))

# Initialisation du modèle1 avec les données
model1 = ClientModel(df)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérifier si l'utilisateur existe et si le mot de passe est correct
        if username in users and users[username] == password:
            session['username'] = username
            flash("Connexion réussie !", "success")
            return redirect(url_for('accueil'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")

    return render_template('login.html')


@app.route('/accueil')
def accueil():
    # Vérifier si l'utilisateur est authentifié
    if 'username' in session:
        username = session['username']
        return render_template('accueil.html', username=username)
    else:
        flash("Vous devez être connecté pour accéder au tableau de bord.", "warning")
        return redirect(url_for('login'))
    
# Les End-point du modèle 1

@app.route('/dashboard')
def dashboard():
    # Vérifier si l'utilisateur est authentifié
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        flash("Vous devez être connecté pour accéder au tableau de bord.", "warning")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Déconnexion réussie", "info")
    return redirect(url_for('login'))


# Route pour obtenir les informations client par MDN
@app.route('/client_info/<mdn>')
def client_info(mdn):
    if model1:
        info = model1.get_client_info(mdn)
        if info["Zone"] is not None:  # Vérifiez si des données valides existent
            return jsonify({"info": info})
        else:
            return jsonify({"error": "MDN non trouvé dans les données"}), 404
    else:
        return jsonify({"error": "Modèle non disponible"}), 500


# Route pour obtenir des clients similaires
@app.route('/similar_clients')
def similar_clients():
    if model1:
        client_index = int(request.args.get('client_index', 0))
        top_n = int(request.args.get('top_n', 5))
        clients = model1.recommander_clients_similaires(client_index, top_n=top_n)
        return jsonify({"clients": clients})
    else:
        return jsonify({"error": "Modèle non disponible"}), 500


# Route pour obtenir les informations de recharge par zone
@app.route('/zone_info/<zone>')
def zone_info(zone):
    if model1:
        frequence = model1.get_frequent_recharge_frequency(zone)
        canal = model1.get_most_used_channel(zone)
        return jsonify({"frequence": frequence, "canal": canal})
    else:
        return jsonify({"error": "Modèle non disponible"}), 500

# Les End-point du modèle 2
@app.route('/index')
def index():
    # Vérifier si l'utilisateur est authentifié
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        flash("Vous devez être connecté pour accéder au tableau de bord.", "warning")
        return redirect(url_for('login'))


# 1. Afficher les zones, leur difficulté de recharge et leur jugement par cluster
@app.route('/get_zones_difficulty_judgment', methods=['GET'])
def get_zones_difficulty_judgment():
    result = df.groupby(['Zone', 'Cluster']).apply(
        lambda x: {
            "Zone": x['Zone'].iloc[0],
            "Cluster": int(x['Cluster'].iloc[0]),  # Conversion en int natif
            "Difficulté_OUI": int((x['Difficulte_recharge'] == 'OUI').sum()),  # Conversion en int natif
            "Difficulté_NON": int((x['Difficulte_recharge'] == 'NON').sum()),  # Conversion en int natif
            "Jugement_Fréquent": x['Jugement_service'].mode()[0] if not x['Jugement_service'].mode().empty else "Non défini"
        }
    ).tolist()
    return jsonify(result)

# 2. Nombre de clients avec ou sans difficulté de recharge par zone
@app.route('/get_clients_by_recharge_difficulty', methods=['GET'])
def get_clients_by_recharge_difficulty():
    stats = df.groupby('Zone').agg(
        Recharge_OUI=('Difficulte_recharge', lambda x: (x == 'OUI').sum()),
        Recharge_NON=('Difficulte_recharge', lambda x: (x == 'NON').sum())
    ).reset_index()

    result = stats.to_dict(orient='records')
    return jsonify(result)

# 3. Nombre de clients ayant ou non un point proche de service par zone
@app.route('/get_clients_by_service_point', methods=['GET'])
def get_clients_by_service_point():
    stats = df.groupby('Zone').agg(
        Point_Proche_OUI=('Point_proche', lambda x: (x == 'OUI').sum()),
        Point_Proche_NON=('Point_proche', lambda x: (x == 'NON').sum())
    ).reset_index()

    result = stats.to_dict(orient='records')
    return jsonify(result)


# 4. Obtenir les jugements fréquents basés sur les critères de l'utilisateur
@app.route('/get_frequent_judgment', methods=['GET'])
def get_frequent_judgment():
    zone = request.args.get('zone')
    difficulty = request.args.get('difficulty')
    point = request.args.get('point')

    # Filtrer les données selon les critères fournis par l'utilisateur
    subset = df[(df['Zone'] == zone) & (df['Difficulte_recharge'] == difficulty) & (df['Point_proche'] == point)]
    if not subset.empty:
        frequent_judgment = subset['Jugement_service'].mode()[0]
        return jsonify({"judgment": frequent_judgment})
    return jsonify({"judgment": "Aucune donnée disponible"})

# 5. Calculer toutes les statistiques combinées pour une vue d'ensemble
@app.route('/get_combined_statistics', methods=['GET'])
def get_combined_statistics():
    combined_stats = df.groupby('Zone').apply(
        lambda x: {
            "Zone": x['Zone'].iloc[0],
            "Recharge_OUI": int((x['Difficulte_recharge'] == 'OUI').sum()),  # Conversion en int natif
            "Recharge_NON": int((x['Difficulte_recharge'] == 'NON').sum()),  # Conversion en int natif
            "Point_Proche_OUI": int((x['Point_proche'] == 'OUI').sum()),  # Conversion en int natif
            "Point_Proche_NON": int((x['Point_proche'] == 'NON').sum()),  # Conversion en int natif
            "Cluster_Details": x.groupby('Cluster').apply(
                lambda y: {
                    "Cluster": int(y['Cluster'].iloc[0]),  # Conversion en int natif
                    "Jugement_Fréquent": y['Jugement_service'].mode()[0] if not y['Jugement_service'].mode().empty else "Non défini"
                }
            ).tolist()
        }
    ).tolist()
    return jsonify(combined_stats)

# 6. Recommandation par zone et cluster (nouveau point ajouté)
@app.route('/get_recommendation', methods=['GET'])
def get_recommendation():
    cluster_id = request.args.get('cluster_id', type=int)
    zone = request.args.get('zone')

    # Filtrer par cluster et zone pour identifier le jugement le plus fréquent
    recommandations = df[(df['Cluster'] == cluster_id) & (df['Zone'] == zone)]
    jugement_freq = recommandations['Jugement_service'].mode()

    if not jugement_freq.empty:
        return jsonify({"recommendation": f"Jugement le plus fréquent pour le cluster {cluster_id} dans la zone {zone}: {jugement_freq.values[0]}"})
    else:
        return jsonify({"recommendation": f"Aucune recommandation disponible pour le cluster {cluster_id} dans la zone {zone}"})

if __name__ == "__main__":
    app.run(debug=True)
