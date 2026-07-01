-- ============================================================================
-- PROJET AES GLOBAL TECH MARKET - STRUCTURE DU DATA WAREHOUSE TARGET
-- Modern Data Stack Open Source - PostgreSQL On-Premise
-- ============================================================================
CREATE USER airflow WITH PASSWORD 'airflow_pass';
CREATE DATABASE airflow_metadata OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow_metadata TO airflow;
-- ----------------------------------------------------------------------------
-- 1. CREATION DES DIMENSIONS CONFORMES (SHARED DIMENSIONS)
-- ----------------------------------------------------------------------------

-- Dimension Temps : Partagée par l'ensemble des tables de faits (via différents rôles)
CREATE TABLE dim_temps (
    id_temps INT PRIMARY KEY, -- Clé intelligente au format numérique YYYYMMDD
    date_complete DATE NOT NULL,
    annee INT NOT NULL,
    trimestre INT NOT NULL,
    mois INT NOT NULL,
    nom_mois VARCHAR(20) NOT NULL,
    semaine_annee INT NOT NULL,
    jour_semaine VARCHAR(15) NOT NULL,
    est_jour_ferie BOOLEAN DEFAULT FALSE
);

-- Dimension Produit : Dénormalisation des tables core_produit, core_categorie et core_marque
CREATE TABLE dim_produit (
    id_produit BIGINT PRIMARY KEY,
    nom_produit VARCHAR(150) NOT NULL,
    code_barre VARCHAR(50),
    categorie_nom VARCHAR(200),
    marque_nom VARCHAR(100),
    prix_vente_actuel DECIMAL(10,2) NOT NULL
);

-- Dimension Boutique & Géographie : Intègre l'arborescence multi-pays (8 pays d'Afrique de l'Ouest)
CREATE TABLE dim_boutique_geographie (
    id_boutique BIGINT PRIMARY KEY,
    nom_boutique VARCHAR(150) NOT NULL,
    adresse TEXT,
    ville_nom VARCHAR(100) NOT NULL,
    pays_nom VARCHAR(100) NOT NULL,
    code_pays VARCHAR(2) NOT NULL,
    est_centre_distribution BOOLEAN DEFAULT FALSE
);

-- Dimension Client Profil : Permet le suivi comportemental et la fidélisation
CREATE TABLE dim_client_profil (
    id_client BIGINT PRIMARY KEY,
    nom_complet VARCHAR(200) NOT NULL,
    email VARCHAR(254),
    ville_nom VARCHAR(100),
    pays_nom VARCHAR(100)
);


-- ----------------------------------------------------------------------------
-- 2. CREATION DES TABLES DE FAITS (CONSTELLATION)
-- ----------------------------------------------------------------------------

-- Fait 1 : Ventes Physiques (Données historiques issues de l'application Tassouma)
CREATE TABLE fait_ventes_boutique (
    id_vente_ligne BIGINT PRIMARY KEY,
    id_produit BIGINT NOT NULL REFERENCES dim_produit(id_produit),
    id_boutique BIGINT NOT NULL REFERENCES dim_boutique_geographie(id_boutique),
    id_client BIGINT NOT NULL REFERENCES dim_client_profil(id_client),
    id_temps_vente INT NOT NULL REFERENCES dim_temps(id_temps),
    quantite INT NOT NULL,
    montant_ht DECIMAL(12,2) NOT NULL,
    montant_tva DECIMAL(12,2) NOT NULL,
    montant_ttc DECIMAL(12,2) NOT NULL,
    cout_achat_total DECIMAL(12,2) NOT NULL,
    marge_brute DECIMAL(12,2) NOT NULL,
    mode_paiement VARCHAR(20) NOT NULL
);

-- Fait 2 : Logistique & Chaîne d'Approvisionnement (Suivi des commandes des boutiques)
CREATE TABLE fait_logistique_approvisionnement (
    id_ligne_commande BIGINT PRIMARY KEY,
    id_produit BIGINT NOT NULL REFERENCES dim_produit(id_produit),
    id_boutique BIGINT NOT NULL REFERENCES dim_boutique_geographie(id_boutique), -- Boutique qui reçoit
    id_temps_commande INT NOT NULL REFERENCES dim_temps(id_temps),
    id_temps_reception INT REFERENCES dim_temps(id_temps),
    quantite_commandee INT NOT NULL,
    quantite_recue INT,
    prix_achat_unitaire DECIMAL(10,2) NOT NULL,
    delai_approvisionnement_jours INT, -- Calculé lors du traitement ETL
    statut_commande VARCHAR(20) NOT NULL
);

-- Fait 3 : Service Après-Vente (Extension requise par le cahier des charges d'entreprise)
CREATE TABLE fait_sav_retours (
    id_retour_ligne BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_produit BIGINT NOT NULL REFERENCES dim_produit(id_produit),
    id_boutique BIGINT NOT NULL REFERENCES dim_boutique_geographie(id_boutique), -- Boutique de dépôt
    id_client BIGINT NOT NULL REFERENCES dim_client_profil(id_client),
    id_temps_depot INT NOT NULL REFERENCES dim_temps(id_temps),
    id_temps_resolution INT REFERENCES dim_temps(id_temps),
    quantite_retournee INT NOT NULL DEFAULT 1,
    cout_reparation_interne DECIMAL(10,2) DEFAULT 0.00,
    statut_resolution VARCHAR(30) NOT NULL -- Ex: 'Echange', 'Réparé', 'Remboursé'
);

-- Fait 4 : Ventes en Ligne (Anticipation de la plateforme unique prévue pour 2027)
CREATE TABLE fait_ventes_en_ligne (
    id_commande_en_ligne BIGINT PRIMARY KEY,
    id_produit BIGINT NOT NULL REFERENCES dim_produit(id_produit),
    id_boutique_livreuse BIGINT NOT NULL REFERENCES dim_boutique_geographie(id_boutique), -- Magasin physique de rattachement
    id_client BIGINT NOT NULL REFERENCES dim_client_profil(id_client),
    id_temps_commande INT NOT NULL REFERENCES dim_temps(id_temps),
    quantite INT NOT NULL,
    montant_ht DECIMAL(12,2) NOT NULL,
    frais_livraison DECIMAL(10,2) NOT NULL,
    statut_livraison VARCHAR(30) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 3. OPTIMISATION : INDEX ANALYTIQUES
-- ----------------------------------------------------------------------------
CREATE INDEX idx_fait_ventes_boutique_temps ON fait_ventes_boutique(id_temps_vente);
CREATE INDEX idx_fait_ventes_boutique_geo ON fait_ventes_boutique(id_boutique);
CREATE INDEX idx_fait_logistique_temps ON fait_logistique_approvisionnement(id_temps_commande);
CREATE INDEX idx_fait_sav_produit ON fait_sav_retours(id_produit);