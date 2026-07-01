#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
PROJET AES GLOBAL TECH MARKET - ORCHESTRATION DU PIPELINE GLOBAL
Auteur: Équipe BI / Plateforme Data (DSI)
Usage: DAG Apache Airflow pour planifier l'ETL et les Jobs d'agrégations
============================================================================
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Importation des modules d'exécution développés dans les dossiers de la Stack
import sys
import os
sys.path.append('/opt/airflow/plugins') # Permet à Airflow de charger les scripts comme plugins

from etl_tassouma_dw import execution_pipeline_etl
from jobs_aggregations import calculer_aggregations_kpis

# ----------------------------------------------------------------------------
# 1. CONFIGURATION DES PARAMÈTRES PAR DÉFAUT DU DAG
# ----------------------------------------------------------------------------
default_args = {
    'owner': 'Equipe_BI_DataPlatform',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email': ['dsi_data@aes-globalmarket.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# ----------------------------------------------------------------------------
# 2. DÉFINITION DU GRAPHE D'ORCHESTRATION (DAG)
# ----------------------------------------------------------------------------
with DAG(
    'dag_bi_global_aes_market',
    default_args=default_args,
    description='Pipeline de synchronisation de la constellation et calcul nocturne des KPIs',
    schedule_interval='0 0 * * *', # Exécution quotidienne à minuit (Fréquence dictionnaire)
    catchup=False,
    tags=['AES_Global', 'Constellation', 'BI', 'Production'],
) as dag:

    # Tâche 1 : Extraction, Transformation et Chargement (ETL) dans PostgreSQL
    task_execution_etl = PythonOperator(
        task_id='execution_pipeline_etl_tassouma',
        python_callable=execution_pipeline_etl,
    )

    # Tâche 2 : Calcul et matérialisation des agrégations métiers et KPIs
    task_calcul_aggregations = PythonOperator(
        task_id='calcul_aggregations_kpis_decisionnels',
        python_callable=calculer_aggregations_kpis,
    )

    # Définition de la dépendance séquentielle : L'ETL doit réussir avant de lancer les agrégations
    task_execution_etl >> task_calcul_aggregations