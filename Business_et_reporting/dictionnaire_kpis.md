# Dictionnaire et Catalogue des KPIs - AES Global Tech Market
**Statut :** Livrable Validé  
**Version :** 1.0 (Production)  
**Validé par :** Direction Data & BI / Direction Financière  

Ce catalogue répertorie les indicateurs clés de performance (KPIs) implémentés dans la solution BI. Chaque calcul est figé au niveau du traitement ETL ou des vues matérialisées pour garantir une source unique de vérité.

---

## 1. Axe Direction Commerciale & Performance Magasins

### KPI 1 : Nombre de Ventes réalisé
* **Description :** Quantité totale de transactions uniques facturées en boutique.
* **Unité :** Nombre (Incrémenté)
* **Fréquence :** Journalière
* **Formule SQL / Règle :** `COUNT(DISTINCT id_vente_ligne)` depuis `fait_ventes_boutique`.
* **Accessibilité :** Libre accès (Toutes directions).

### KPI 2 : Chiffre d'Affaires Hors Taxes (CA HT)
* **Description :** Total des revenus générés par les ventes, net de taxes.
* **Unité :** Monétaire (XOF / GNFs / Nairas)
* **Fréquence :** Journalière
* **Formule SQL / Règle :** `SUM(montant_ht)` depuis `fait_ventes_boutique`.
* **Accessibilité :** Libre accès.

### KPI 3 : Volume d'Articles Vendus
* **Description :** Somme cumulée des pièces technologiques vendues en boutique.
* **Unité :** Quantité (Unités)
* **Fréquence :** Journalière
* **Formule SQL / Règle :** `SUM(quantite)` depuis `fait_ventes_boutique`.
* **Accessibilité :** Libre accès.

### KPI 4 : Panier Moyen HT
* **Description :** Montant moyen dépensé par un client particulier lors d'une transaction.
* **Unité :** Monétaire
* **Fréquence :** Hebdomadaire / Mensuelle
* **Formule SQL / Règle :** `SUM(montant_ht) / COUNT(DISTINCT id_vente_ligne)`
* **Accessibilité :** Libre accès.

### KPI 5 : Croissance du CA par Pays / Ville
* **Description :** Évolution en pourcentage du Chiffre d'Affaires comparativement à la période précédente (N-1).
* **Unité :** Pourcentage (%)
* **Fréquence :** Mensuelle / Annuelle
* **Formule SQL / Règle :** `((CA_Periode_Actuelle - CA_Periode_Precedente) / CA_Periode_Precedente) * 100`
* **Accessibilité :** Direction Générale, CFO, Country Managers.

---

## 2. Axe Direction Financière (Accès Restreint)

### KPI 6 : Coût d'Achat Total Historique
* **Description :** Évaluation de la valeur d'acquisition d'origine des produits vendus.
* **Unité :** Monétaire
* **Fréquence :** Hebdomadaire
* **Formule SQL / Règle :** `SUM(cout_achat_total)` recalculé à partir de la ligne de vente.
* **Accessibilité :** Restreint Finance / Direction Générale.

### KPI 7 : Marge Brute Totale
* **Description :** Gain financier réalisé après déduction du coût de revient des marchandises.
* **Unité :** Monétaire
* **Fréquence :** Hebdomadaire / Mensuelle
* **Formule SQL / Règle :** `SUM(marge_brute)` où `marge_brute = montant_ht - cout_achat_total`.
* **Accessibilité :** Restreint Finance.

### KPI 8 : Taux de Marge Commerciale
* **Description :** Rentabilité d'une boutique ou d'une catégorie de produit par rapport au chiffre d'affaires généré.
* **Unité :** Pourcentage (%)
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `(SUM(marge_brute) / SUM(montant_ht)) * 100`
* **Accessibilité :** Restreint Finance / Country Managers.

### KPI 9 : Montant Consolidé de la TVA collectée
* **Description :** Cumul des taxes sur la valeur ajoutée collectées pour reversement fiscal par filiale nationale.
* **Unité :** Monétaire
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `SUM(montant_tva)` géré par l'ETL (selon taux local).
* **Accessibilité :** Direction Financière Groupe et Responsable Financier Pays.

---

## 3. Axe Direction Logistique & Supply Chain

### KPI 10 : Taux de Rupture de Stock Magasin
* **Description :** Fréquence des produits tombés en dessous du seuil d'alerte critique.
* **Unité :** Pourcentage (%)
* **Fréquence :** Journalière
* **Formule SQL / Règle :** `(Nombre de références où stock <= seuil_alerte / Nombre total de références actives) * 100`
* **Accessibilité :** Logistique, Supply Chain, Boutique Managers.

### KPI 11 : Délai Moyen de Réapprovisionnement (Lead Time)
* **Description :** Temps moyen mis entre l'émission d'une commande par une boutique et sa réception physique.
* **Unité :** Nombre de jours
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `AVG(delai_approvisionnement_jours)` depuis `fait_logistique_approvisionnement`.
* **Accessibilité :** Logistique & Supply Chain.

### KPI 12 : Volume de Commandes Internes Émises
* **Description :** Activité d'approvisionnement globale des magasins vers les centres de distribution régionaux.
* **Unité :** Nombre (Commandes)
* **Fréquence :** Hebdomadaire
* **Formule SQL / Règle :** `COUNT(DISTINCT id_ligne_commande)`
* **Accessibilité :** Logistique & Supply Chain.

### KPI 13 : Taux de Service Fournisseur Interne (Fill Rate)
* **Description :** Pourcentage des quantités de produits effectivement reçues par rapport aux quantités commandées par la boutique.
* **Unité :** Pourcentage (%)
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `(SUM(quantite_recue) / SUM(quantite_commandee)) * 100`
* **Accessibilité :** Logistique & Supply Chain.

---

## 4. Axe Service Après-Vente (SAV) & Expérience Client

### KPI 14 : Taux de Retour SAV (Fiabilité Produits)
* **Description :** Proportion de produits High Tech retournés pour défaillance technique.
* **Unité :** Pourcentage (%)
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `(SUM(f.quantite_retournee) / SUM(v.quantite)) * 100` groupé par produit/marque.
* **Accessibilité :** Libre accès.

### KPI 15 : Coût Global des Réparations Internes
* **Description :** Somme financière absorbée par la prise en charge technique sous garantie.
* **Unité :** Monétaire
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `SUM(cout_reparation)` depuis `fait_sav_retours`.
* **Accessibilité :** Finance & Directeurs Pays.

### KPI 16 : Délai Moyen de Résolution SAV
* **Description :** Durée moyenne d'immobilisation d'un appareil entre son dépôt et sa remise au client.
* **Unité :** Nombre de jours
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `AVG(id_temps_resolution - id_temps_depot)` converti en jours.
* **Accessibilité :** Direction Marketing & Expérience Client.

---

## 5. Axe Anticipation Digitale (E-Commerce 2027)

### KPI 17 : Volume des Ventes en Ligne (Anticipation)
* **Description :** Volume de commandes passées via la future plateforme Web unique.
* **Unité :** Nombre
* **Fréquence :** Temps réel (Dès déploiement 2027)
* **Formule SQL / Règle :** `COUNT(DISTINCT id_commande_en_ligne)` depuis `fait_ventes_en_ligne`.
* **Accessibilité :** Libre accès.

### KPI 18 : Chiffre d'Affaires Digital Réparti par Boutique
* **Description :** CA Web réattribué aux boutiques physiques gérant la livraison locale.
* **Unité :** Monétaire
* **Fréquence :** Hebdomadaire
* **Formule SQL / Règle :** `SUM(montant_ht)` depuis `fait_ventes_en_ligne` groupé par `id_boutique_livreuse`.
* **Accessibilité :** Direction Commerciale Groupe & CFO.

### KPI 19 : Part du Chiffre d'Affaires Digital dans le CA Global
* **Description :** Indicateur de pénétration des ventes en ligne dans la stratégie omnicanale.
* **Unité :** Pourcentage (%)
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `(SUM(CA_en_ligne) / (SUM(CA_en_ligne) + SUM(CA_boutique))) * 100`
* **Accessibilité :** Direction Générale & CFO.

### KPI 20 : Coût Moyen de Livraison à Domicile
* **Description :** Frais logistiques facturés pour le transport de la commande web.
* **Unité :** Monétaire
* **Fréquence :** Mensuelle
* **Formule SQL / Règle :** `AVG(frais_livraison)` depuis `fait_ventes_en_ligne`.
* **Accessibilité :** Logistique & Supply Chain.