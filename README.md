<p align="center">
    <img src="images/logo.png" width="200" alt="Logo du Projet">
</p>

# Système de Gestion de Sondages et Analyse Prédictive par Machine Learning

### Présentation du Projet
Ce projet, développé dans le cadre de travaux de recherche en Ingénierie des Données et Intelligence Artificielle, consiste en une API REST robuste conçue pour automatiser le traitement des sondages. Au-delà de la simple collecte, la plateforme intègre des modèles d'apprentissage automatique pour transformer les données brutes en informations stratégiques exploitables.

---

## Architecture Visuelle et Interfaces

### Accès et Sécurisation
Le système dispose d'une interface d'authentification sécurisée garantissant l'intégrité des données collectées et la restriction des accès aux seuls administrateurs autorisés.
<p align="center">
    <img src="images/login.png" width="850" alt="Interface d'authentification">
</p>

### Tableau de Bord Principal (Accueil)
L'interface d'accueil centralise la gestion des enquêtes actives, permettant une surveillance en temps réel des flux de données entrants et des métriques de complétion.
<p align="center">
    <img src="images/accueil.png" width="850" alt="Interface d'accueil et gestion">
</p>

### Analyse de Données et Clustering (Modèle 1)
Le premier module analytique repose sur des algorithmes de clustering (segmentation) permettant de regrouper les répondants par profils de comportement homogènes.
<p align="center">
    <img src="images/model1.png" width="850" alt="Analyse par Clustering">
</p>

### Moteur de Recommandation (Modèle 2)
Le second module exploite des modèles prédictifs pour générer des recommandations automatiques basées sur les tendances extraites, facilitant ainsi la prise de décision.
<p align="center">
    <img src="images/model2.png" width="850" alt="Moteur de Recommandation">
</p>

---

## Spécifications Fonctionnelles

1. **Ingénierie des Données** : Nettoyage, normalisation et prétraitement automatisé des réponses aux sondages.
2. **Segmentation Avancée** : Mise en œuvre d'algorithmes de type K-Means ou DBSCAN pour l'identification de clusters de répondants.
3. **Système Expert de Recommandation** : Algorithmes basés sur l'apprentissage supervisé pour l'analyse des corrélations et la prédiction de tendances.
4. **API RESTful** : Architecture modulaire permettant l'intégration facile avec d'autres systèmes tiers.

## Spécifications Techniques

- **Backend** : Python 3.10+, Flask Framework.
- **Data Science** : Scikit-learn, Pandas, NumPy, Scipy.
- **Visualisation** : Matplotlib, Seaborn, Chart.js.
- **Base de Données** : SQLite / MySQL pour la persistance des données et des modèles.
- **Déploiement** : Architecture compatible avec les environnements Cloud (AWS / Heroku).

## Installation et Configuration

1. **Clonage du projet** :
   ```bash
   git clone https://github.com/lassana99/api-gestion-sondages-ml.git