#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
PROJET AES GLOBAL TECH MARKET - CALCULS DES AGREGATIONS ET KPIS
Auteur: Équipe Direction BI
Usage: Traitement analytique du Data Warehouse (PostgreSQL) -> Tables d'agrégations
============================================================================
"""

import sys
import pandas as pd
from sqlalchemy import create_engine

# Connexion locale au Data Warehouse PostgreSQL On-Premise
URL_DW = "postgresql+psycopg2://postgres:password@localhost:5432/aes_bi_dw"


def calculer_aggregations_kpis():
    """Calcule les indicateurs clés et matérialise les tables agrégées"""
    try:
        print("[AGREGATION] Connexion au Data Warehouse analytique...")
        engine = create_engine(URL_DW)
        
        # 1. Extraction des faits de ventes bruts et des dimensions géographiques
        print("[AGREGATION] Récupération des données transactionnelles historisées...")
        requete_ventes = """
            SELECT 
                f.id_boutique, 
                f.id_temps_vente, 
                f.quantite, 
                f.montant_ht, 
                f.cout_achat_total, 
                f.marge_brute,
                b.nom_boutique,
                b.pays_nom,
                b.ville_nom
            FROM fait_ventes_boutique f
            JOIN dim_boutique_geographie b ON f.id_boutique = b.id_boutique
        """
        df_ventes = pd.read_sql(requete_ventes, engine)
        
        if df_ventes.empty:
            print("[AGREGATION] Attention : La table 'fait_ventes_boutique' est vide. Fin du job.")
            return

        # 2. Calcul et regroupement selon le catalogue des KPIs (Maille : Boutique / Jour)
        print("[AGREGATION] Alignement avec le dictionnaire des KPIs (KPI 1, KPI 2, KPI 3)...")
        
        # Regroupement analytique
        df_agreg_journaliere = df_ventes.groupby(['id_boutique', 'nom_boutique', 'ville_nom', 'pays_nom', 'id_temps_vente']).agg(
            kpi_1_nombre_ventes=('quantite', 'count'),                        # KPI 1 : Libre accès
            kpi_2_chiffre_affaires_ht=('montant_ht', 'sum'),                  # KPI 2 : Libre accès
            kpi_3_marge_brute_totale=('marge_brute', 'sum'),                  # KPI 3 : RESTREINT FINANCE
            volume_articles_vendus=('quantite', 'sum')
        ).reset_index()
        
        # Calcul du taux de marge moyen par boutique / jour pour enrichir l'analyse financière
        df_agreg_journaliere['taux_marge_moyen'] = (
            df_agreg_journaliere['kpi_3_marge_brute_totale'] / df_agreg_journaliere['kpi_2_chiffre_affaires_ht']
        ).fillna(0) * 100

        # 3. Écriture de la table d'agrégation finale (Idéal pour les performances d'Apache Superset)
        print("[AGREGATION] Matérialisation de la table de performance globale...")
        df_agreg_journaliere.to_sql(
            'aggr_performance_magasin_journalier', 
            engine, 
            if_exists='replace', 
            index=False
        )
        
        print(" -> Table 'aggr_performance_magasin_journalier' créée et indexée.")
        print("[AGREGATION] Traitement analytique terminé avec succès.")

    except Exception as error:
        print(f"\n[ERREUR AGREGATION] Échec lors du calcul des indicateurs : {str(error)}")
        sys.exit(1)


if __name__ == "__main__":
    calculer_aggregations_kpis()