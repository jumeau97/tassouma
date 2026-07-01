#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
PROJET AES GLOBAL TECH MARKET - CALCULS DES AGREGATIONS ET KPIS (OPTIMISÉ)
Auteur: Équipe Direction BI
Usage: Traitement analytique du Data Warehouse (PostgreSQL) -> Tables d'agrégations
============================================================================
"""

import sys
from sqlalchemy import create_engine, text

# Connexion locale au Data Warehouse PostgreSQL On-Premise
URL_DW = "postgresql+psycopg2://postgres:postgres@aes_postgres_dw:5432/aes_bi_dw"


def calculer_aggregations_kpis():
    """Calcule les indicateurs clés directement en SQL pour éviter les crashs de mémoire (OOM)"""
    try:
        print("[AGREGATION] Connexion au Data Warehouse analytique...")
        engine = create_engine(URL_DW)
        
        print("[AGREGATION] Calcul et matérialisation de la table de performance globale sur PostgreSQL...")
        
        # Requête optimisée : Le calcul (Group By, Jointures, Agrégations) est délégué à Postgres
        requete_materialisation = """
            CREATE TABLE IF NOT EXISTS aggr_performance_magasin_journalier_temp AS
            SELECT 
                f.id_boutique, 
                b.nom_boutique, 
                b.ville_nom, 
                b.pays_nom, 
                f.id_temps_vente,
                COUNT(f.quantite) AS kpi_1_nombre_ventes,
                SUM(f.montant_ht) AS kpi_2_chiffre_affaires_ht,
                SUM(f.marge_brute) AS kpi_3_marge_brute_totale,
                SUM(f.quantite) AS volume_articles_vendus,
                CASE 
                    WHEN SUM(f.montant_ht) > 0 THEN (SUM(f.marge_brute) / SUM(f.montant_ht)) * 100
                    ELSE 0 
                END AS taux_marge_moyen
            FROM fait_ventes_boutique f
            JOIN dim_boutique_geographie b ON f.id_boutique = b.id_boutique
            GROUP BY f.id_boutique, b.nom_boutique, b.ville_nom, b.pays_nom, f.id_temps_vente;
            
            -- Remplacement sécurisé équivalent à if_exists='replace'
            DROP TABLE IF EXISTS aggr_performance_magasin_journalier;
            ALTER TABLE aggr_performance_magasin_journalier_temp RENAME TO aggr_performance_magasin_journalier;
        """
        
        with engine.connect() as conn:
            conn.execute(text(requete_materialisation))
            
        print(" -> Table 'aggr_performance_magasin_journalier' créée et indexée sur PostgreSQL.")
        print("[AGREGATION] Traitement analytique terminé avec succès.")

    except Exception as error:
        print(f"\n[ERREUR AGREGATION] Échec lors du calcul des indicateurs : {str(error)}")
        sys.exit(1)


if __name__ == "__main__":
    calculer_aggregations_kpis()