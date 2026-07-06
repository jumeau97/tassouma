# 🛠️ Commandes Opérationnelles - Stack BI

### 1. Lancement de l'Infrastructure
```bash
# Configuration initiale : Allouer 6 Go à 8 Go de RAM dans Docker Desktop (Section Resources)
# Lancer et construire tous les conteneurs en arrière-plan
docker compose up -d --build

# Vérifier le statut des conteneurs
docker compose ps

#importer le fichier dump
docker exec -i aes_mysql_oltp mysql -u root -p"password" tassouma_oltp < projetbi.sql
#verifier les tables
docker exec -it aes_mysql_oltp mysql -u root -p"password" -e "SHOW TABLES FROM tassouma_oltp;"
#supprimer une table par exemple
docker exec -it aes_mysql_oltp mysql -u root -p"password" -e "DROP TABLE IF EXISTS tassouma_oltp.core_vente;"
# Orchestration et Tests Rapiéde (Airflow CLI)
# Étape A : Vider le cache et réinitialiser les statuts du DAG
docker exec -it aes_airflow_scheduler airflow tasks clear -d dag_bi_global_aes_market -X -R

# Étape B : Tester la phase d'ETL (Extraction MySQL -> PostgreSQL)
docker exec -it aes_airflow_scheduler airflow tasks test dag_bi_global_aes_market execution_pipeline_etl_tassouma 2026-06-30

# Étape C : Tester la phase d'Agrégation (Calcul SQL des KPIs Décisionnels)
docker exec -it aes_airflow_scheduler airflow tasks test dag_bi_global_aes_market calcul_aggregations_kpis_decisionnels 2026-06-30

# Étape D : Suivre l'état des runs globaux
docker exec -it aes_airflow_scheduler airflow dags list-runs -d dag_bi_global_aes_market
# Maintenance et Débuggage

# Consulter les logs système en direct
docker logs -f aes_airflow_scheduler

# Purger le cache d'exécution Python (__pycache__)
docker exec -it aes_airflow_scheduler rm -rf /opt/airflow/dags/__pycache__/

# Recréer à chaud le service Scheduler
docker compose up -d --force-recreate airflow-scheduler


# Inspecter le Data Warehouse (PostgreSQL Cible)
docker exec -it aes_postgres_dw psql -U postgres -d aes_bi_dw -c "SELECT * FROM aggr_performance_magasin_journalier LIMIT 10;"

# Inspecter l'Application Source (MySQL OLTP)
docker exec -it mysql_oltp mysql -u root -p'password' tassouma_oltp -e "SHOW TABLES;"


# Par l'Interface Graphique (Web UI)
# C'est le moyen le plus simple pour piloter vos DAGs, voir l'état des tâches et consulter les logs graphiquement.

# URL par défaut : Ouvrez votre navigateur et accédez à http://localhost:8080

# Identifiants standards (si configurés par défaut) :

# Username : airflow

# Password : airflow

# Ouvrir une session interactive (Terminal) dans le conteneur :
# docker exec -it aes_airflow_scheduler bash

# docker exec -it aes_airflow_scheduler airflow dags list

#CREER DIRECTEMENT LA BD DANS SUPERSET
docker exec -it aes_bi_superset superset set-database-uri \
  --database_name "PostgreSQL_DW" \
  --uri "postgresql+psycopg2://postgres:postgres@aes_postgres_dw:5432/airflow_metadata"

#   Le terme DAG signifie Directed Acyclic Graph (Graphe Orienté Acyclique).

#   En clair, pour la DSI et l'équipe BI, le DAG est le chef d'orchestre automatisé de toute votre plateforme Data. C'est lui qui s'assure que les scripts s'exécutent tout seuls, dans le bon ordre, à la bonne heure, et qui vous alerte en cas de panne.

# Problématique : Les données de ventes, de stocks et d'achats sont cloisonnées par boutique ou par pays. La direction n'a pas de vision consolidée et instantanée des performances.

# Objectif BI : Mettre en place un entrepôt de données (Data Warehouse) centralisé et automatiser un pipeline ETL nocturne pour alimenter des dashboards visuels et interactifs sous Apache Superset.