# Modèle de Gouvernance de la Data - AES Global Tech Market
**Statut :** Livrable Validé  
**Auteur :** Équipe BI / Consultant BI  
**Date :** Juin 2026  

Ce document définit les rôles, les responsabilités et la politique de sécurité d'accès aux données de la constellation du Data Warehouse (PostgreSQL) en accord avec l'organigramme du groupe.

---

## 1. Classification de la Sensibilité des Données

Pour protéger les indicateurs stratégiques d'AES Global Tech Market, la donnée est segmentée en deux niveaux de confidentialité :
* **Niveau 1 : Visibilité Libre (Public Interne) :** Volumes de ventes, quantités de stocks, délais logistiques, nombres de retours SAV, volumes de commandes en ligne.
* **Niveau 2 : Visibilité Restreinte (Confidentiel Finance) :** Prix d'achat unitaire, coût d'achat total, marges brutes, taux de marge par boutique, pays ou marque.

---

## 2. Matrice des Profils et Droits d'Accès (RACLI)

L'accès à l'architecture Modern Data Stack (Jupyter Lab, Apache Airflow, Apache Superset) est régi par la matrice de profils suivante :

### A. Utilisateurs Techniques (Profils Analytiques R&D)
* **Data Scientists & Data Analysts (Direction Data & BI) :**
    * *Usage :* Modélisation prédictive de la demande (Stocks/Logistique) et segmentation client.
    * *Outils :* Jupyter Lab, requêtes SQL directes sur PostgreSQL, Apache Superset.
    * *Droits :* Lecture totale sur l'ensemble de la constellation (Faits et Dimensions), y compris les données financières de Niveau 2.
* **Plateforme Data (DSI - Administrateurs) :**
    * *Usage :* Maintenance technique de l'infrastructure, gestion des pipelines ETL et monitoring.
    * *Outils :* Apache Airflow, Docker, PostgreSQL (Accès Administrateur).
    * *Droits :* Lecture/Écriture et DDL sur toutes les tables. Aucun droit de regard sur l'interprétation métier des données financières.

### B. Utilisateurs Business (Sans Compétences SQL)
Ces utilisateurs consomment la donnée exclusivement à travers l'interface visuelle et sans code d'**Apache Superset**.

* **Direction Générale (CEO) & Direction Financière (CFO / Contrôle de Gestion) :**
    * *Usage :* Pilotage de la performance globale et consolidation multi-pays.
    * *Périmètre :* Vision **Groupe complète**. Accès total Niveau 1 et Niveau 2 (Chiffre d'Affaires et Marges).
* **Direction Logistique & Supply Chain :**
    * *Usage :* Optimisation des niveaux de stocks et réduction des ruptures de reapprovisionnement.
    * *Périmètre :* Vision **Logistique complète** (Fait_Logistique_Approvisionnement). Accès uniquement aux données de Niveau 1. Pas d'accès aux marges.
* **Direction Commerciale Groupe & Direction Marketing :**
    * *Usage :* Suivi des ventes en boutique, performances des campagnes promotionnelles et analyse SAV.
    * *Périmètre :* Vision **Ventes et SAV globale**. Accès restreint aux indicateurs de Niveau 1 (Volume de ventes, chiffre d'affaires HT). Pas d'accès à la marge brute.
* **Directeurs Pays (Country Managers) :**
    * *Usage :* Pilotage de la filiale nationale (Ex: Mali, Côte d'Ivoire).
    * *Périmètre :* Filtre de sécurité dynamique (Row-Level Security) restreint à leur **Pays unique**. Accès au Niveau 1 et Niveau 2 pour leur pays respectif.
* **Managers de Magasin (Boutique Managers) :**
    * *Usage :* Gestion des stocks locaux, suivi quotidien des caisses et techniciens SAV.
    * *Périmètre :* Filtre de sécurité dynamique restreint à leur **Boutique unique**. Accès strict Niveau 1 (Pas de visibilité sur les marges globales ou les prix d'achat fournisseurs).

---

## 3. Règles d'Assurance Qualité et Conformité (DSI)

1.  **Dénormalisation Métier :** Aucun calcul financier ou d'agrégation ne doit être effectué en direct par un outil de visualisation. Tout calcul (TVA, Marge) doit être figé en amont par le pipeline ETL (`etl_tassouma_dw.py`) pour garantir qu'un seul chiffre officiel circule dans l'entreprise.
2.  **Masquage RGPD / Sécurité :** Les données des clients particuliers (`dim_client_profil`) ne contiennent aucun mot de passe, clé d'authentification ou coordonnées bancaires. Seuls le nom, l'email et la géographie sont conservés à des fins d'analyse de fidélisation par la Direction Marketing.