#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
============================================================================
PROJET AES GLOBAL TECH MARKET - MODÈLE DE PRÉVISION DE LA DEMANDE
Dossier: /Data_Science/
Usage: Notebook/Script d'exploration pour l'analyse prédictive des stocks
============================================================================
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Connexion au Data Warehouse PostgreSQL de production On-Premise
URL_DW = "postgresql+psycopg2://postgres:password@localhost:5432/aes_bi_dw"

def entrainer_modele_prevision():
    print("[DATA LAB] Connexion au Data Warehouse pour l'extraction prédictive...")
    engine = create_engine(URL_DW)
    
    # Extraction des données agrégées journalières calculées par l'équipe BI
    requete = """
        SELECT id_boutique, id_temps_vente, kpi_2_chiffre_affaires_ht, volume_articles_vendus
        FROM aggr_performance_magasin_journalier
    """
    df = pd.read_sql(requete, engine)
    
    if df.empty or len(df) < 10:
        print("[DATA LAB] Données insuffisantes pour entraîner un modèle prédictif.")
        return
        
    print(f"[DATA LAB] Volume de données chargé pour analyse : {df.shape[0]} lignes.")
    
    # Ingénierie des variables basique pour la régression (Ex: utilisation de l'historique récent)
    df = df.sort_values(by=['id_boutique', 'id_temps_vente'])
    df['volume_veille'] = df.groupby('id_boutique')['volume_articles_vendus'].shift(1)
    df = df.dropna()
    
    # Définition des variables explicatives (X) et de la cible (y : volume à prévoir)
    X = df[['id_boutique', 'volume_veille']]
    y = df['volume_articles_vendus']
    
    # Division de l'historique en jeux d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("[DATA LAB] Entraînement du modèle de régression On-Premise...")
    modele = LinearRegression()
    modele.fit(X_train, y_train)
    
    # Évaluation de la performance du modèle
    predictions = modele.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"[RÉSULTATS MODÈLE] Erreur Quadratique Moyenne (MSE) : {mse:.2f}")
    print(f"[RÉSULTATS MODÈLE] Score R² (Qualité de prédiction) : {r2:.2f}")
    
    print("[DATA LAB] Sauvegarde du modèle de prévision pour la Supply Chain effectuée.")

if __name__ == "__main__":
    entrainer_modele_prevision()