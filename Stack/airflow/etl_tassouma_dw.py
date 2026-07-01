#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
PROJET AES GLOBAL TECH MARKET - PIPELINE ETL PRINCIPAL
Auteur: Équipe BI
Usage: Extraction depuis l'OLTP (MySQL) -> Transformation -> Chargement (PostgreSQL)
============================================================================
"""

import sys
import pandas as pd
from sqlalchemy import create_engine, text

# ----------------------------------------------------------------------------
# 1. CONFIGURATIONS DES CHAINES DE CONNEXION (INTER-CONTENEURS DOCKER)
# ----------------------------------------------------------------------------
# Source: Application Tassouma (MySQL dans son conteneur dédié)
URL_SOURCE_OLTP = "mysql+pymysql://root:password@aes_mysql_oltp:3306/tassouma_oltp"

# Destination: Data Warehouse Global (PostgreSQL dans son conteneur dédié)
URL_CIBLE_DW = "postgresql+psycopg2://postgres:password@aes_postgres_dw:5432/aes_bi_dw"


def execution_pipeline_etl():
    """Fonction principale exécutant les phases E-T-L du projet"""
    try:
        print("[ETL] Initialisation des moteurs de bases de données...")
        engine_src = create_engine(URL_SOURCE_OLTP)
        engine_dw = create_engine(URL_CIBLE_DW)
        
        # --------------------------------------------------------------------
        # PHASE 1 : EXTRACTION (E)
        # --------------------------------------------------------------------
        print("[ETL - PHASE 1] Extraction des tables sources depuis Tassouma (MySQL)...")
        
        df_ventes = pd.read_sql("SELECT * FROM core_vente", engine_src)
        df_lignes_vente = pd.read_sql("SELECT * FROM core_lignevente", engine_src)
        df_produits = pd.read_sql("SELECT * FROM core_produit", engine_src)
        df_marques = pd.read_sql("SELECT * FROM core_marque", engine_src)
        df_categories = pd.read_sql("SELECT * FROM core_categorie", engine_src)
        df_boutiques = pd.read_sql("SELECT * FROM core_boutique", engine_src)
        df_villes = pd.read_sql("SELECT * FROM core_ville", engine_src)
        df_pays = pd.read_sql("SELECT * FROM core_pays", engine_src)
        df_clients = pd.read_sql("SELECT * FROM core_client", engine_src)
        df_commandes_achat = pd.read_sql("SELECT * FROM core_commandeachat", engine_src)
        df_lignes_achat = pd.read_sql("SELECT * FROM core_lignecommandeachat", engine_src)

        # --------------------------------------------------------------------
        # PHASE 2 : TRANSFORMATION & ALIMENTATION DES DIMENSIONS (T)
        # --------------------------------------------------------------------
        print("[ETL - PHASE 2] Transformation et chargement des dimensions conformes...")

        # A. Dimension Produit
        df_p_m = pd.merge(df_produits, df_marques, left_on='marque_id', right_on='id', suffixes=('', '_m'))
        df_p_m_c = pd.merge(df_p_m, df_categories, left_on='categorie_id', right_on='id', suffixes=('', '_c'))
        
        dim_produit = df_p_m_c[['id', 'nom', 'code_barre', 'nom_c', 'nom_m', 'prix_vente']].rename(columns={
            'id': 'id_produit', 'nom': 'nom_produit', 'nom_c': 'categorie_nom', 
            'nom_m': 'marque_nom', 'prix_vente': 'prix_vente_actuel'
        })
        dim_produit.to_sql('dim_produit', engine_dw, if_exists='append', index=False)
        print(" -> Dimension 'dim_produit' alimentée.")

        # B. Dimension Boutique & Géographie
        df_b_v = pd.merge(df_boutiques, df_villes, left_on='ville_id', right_on='id', suffixes=('', '_v'))
        df_b_v_p = pd.merge(df_b_v, df_pays, left_on='pays_id', right_on='id', suffixes=('', '_p'))
        
        # Identification des centres régionaux basés sur l'historique logistique
        centres_ids = df_commandes_achat['centre_id'].dropna().unique()
        df_b_v_p['est_centre_distribution'] = df_b_v_p['id'].isin(centres_ids)
        
        dim_boutique = df_b_v_p[['id', 'nom', 'adresse', 'nom_v', 'nom_p', 'code', 'est_centre_distribution']].rename(columns={
            'id': 'id_boutique', 'nom': 'nom_boutique', 'nom_v': 'ville_nom', 'nom_p': 'pays_nom', 'code': 'code_pays'
        })
        dim_boutique.to_sql('dim_boutique_geographie', engine_dw, if_exists='append', index=False)
        print(" -> Dimension 'dim_boutique_geographie' alimentée.")

        # C. Dimension Client
        df_cl_v = pd.merge(df_clients, df_villes, left_on='ville_id', right_on='id', suffixes=('', '_v'))
        df_cl_v_p = pd.merge(df_cl_v, df_pays, left_on='pays_id', right_on='id', suffixes=('', '_p'))
        
        dim_client = df_cl_v_p[['id', 'nom', 'email', 'nom_v', 'nom_p']].rename(columns={
            'id': 'id_client', 'nom': 'nom_complet', 'nom_v': 'ville_nom', 'nom_p': 'pays_nom'
        })
        dim_client.to_sql('dim_client_profil', engine_dw, if_exists='append', index=False)
        print(" -> Dimension 'dim_client_profil' alimentée.")

        # --------------------------------------------------------------------
        # PHASE 3 : TRANSFORMATION & ALIMENTATION DES FAITS (L)
        # --------------------------------------------------------------------
        print("[ETL - PHASE 3] Calcul des métriques métiers et chargement des tables de faits...")

        # --- FAIT 1 : VENTES BOUTIQUE ---
        df_sales_flat = pd.merge(df_lignes_vente, df_ventes, left_on='vente_id', right_on='id', suffixes=('_l', '_e'))
        
        # Implémentation des règles de gestion financières non stockées en base
        df_sales_flat['montant_ht'] = df_sales_flat['quantite'] * df_sales_flat['prix_unitaire']
        # Simulation d'un taux de TVA standard à 18% (adaptable par pays)
        df_sales_flat['montant_tva'] = df_sales_flat['montant_ht'] * 0.18
        df_sales_flat['montant_ttc'] = df_sales_flat['montant_ht'] + df_sales_flat['montant_tva']
        df_sales_flat['cout_achat_total'] = df_sales_flat['quantite'] * df_sales_flat['prix_achat']
        df_sales_flat['marge_brute'] = df_sales_flat['montant_ht'] - df_sales_flat['cout_achat_total']
        
        # Mapping de la clé de la dimension temps (Format numérique YYYYMMDD)
        df_sales_flat['id_temps_vente'] = pd.to_datetime(df_sales_flat['created_at_e']).dt.strftime('%Y%m%d').astype(int)
        # Mode de paiement par défaut si non spécifié
        if 'mode_paiement' not in df_sales_flat.columns:
            df_sales_flat['mode_paiement'] = 'Espèces'

        fait_ventes = df_sales_flat[[
            'id_l', 'produit_id', 'boutique_id', 'client_id', 'id_temps_vente',
            'quantite', 'montant_ht', 'montant_tva', 'montant_ttc', 'cout_achat_total', 'marge_brute', 'mode_paiement'
        ]].rename(columns={
            'id_l': 'id_vente_ligne', 'produit_id': 'id_produit', 'boutique_id': 'id_boutique', 'client_id': 'id_client'
        })
        
        fait_ventes.to_sql('fait_ventes_boutique', engine_dw, if_exists='append', index=False)
        print(" -> Table de faits 'fait_ventes_boutique' chargée avec succès.")

        # --- FAIT 2 : LOGISTIQUE & APPROVISIONNEMENT ---
       # --- FAIT 2 : LOGISTIQUE & APPROVISIONNEMENT ---
        df_log_flat = pd.merge(df_lignes_achat, df_commandes_achat, left_on='commande_id', right_on='id', suffixes=('_l', '_e'))
        
        df_log_flat['id_temps_commande'] = pd.to_datetime(df_log_flat['created_at_e']).dt.strftime('%Y%m%d').astype(int)
        
        # 1. On utilise 'updated_at_e' comme date de traitement/réception effective de la commande
        date_reception_conv = pd.to_datetime(df_log_flat['updated_at_e'], errors='coerce')
        
        # 2. Assignation propre de la clé de temps (AAAAMMJJ) gérant le cas des commandes en attente
        df_log_flat['id_temps_reception'] = date_reception_conv.dt.strftime('%Y%m%d').astype('Int64')

        # 3. Calcul du délai d'approvisionnement (Mise à jour - Création)
        delta_days = (date_reception_conv - pd.to_datetime(df_log_flat['created_at_e'])).dt.days
        df_log_flat['delai_approvisionnement_jours'] = delta_days.astype('Int64')
        
        # Quantité reçue (si la commande est validée)
        if 'quantite_recue' not in df_log_flat.columns:
            df_log_flat['quantite_recue'] = df_log_flat['quantite']

        fait_logistique = df_log_flat[[
            'id_l', 'produit_id', 'boutique_id', 'id_temps_commande', 'id_temps_reception',
            'quantite', 'quantite_recue', 'prix_achat', 'delai_approvisionnement_jours', 'statut'
        ]].rename(columns={
            'id_l': 'id_ligne_commande', 'produit_id': 'id_produit', 'boutique_id': 'id_boutique',
            'prix_achat': 'prix_achat_unitaire', 'statut': 'statut_commande'
        })

        fait_logistique.to_sql('fait_logistique_approvisionnement', engine_dw, if_exists='append', index=False)
        print(" -> Table de faits 'fait_logistique_approvisionnement' chargée avec succès.")
        
        print("\n[ETL] Exécution globale terminée. Données chargées dans la constellation.")

    except Exception as error:
        print(f"\n[ERREUR ETL] Une erreur est survenue durant le traitement : {str(error)}")
        sys.exit(1)


if __name__ == "__main__":
    execution_pipeline_etl()