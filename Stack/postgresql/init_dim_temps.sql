-- ============================================================================
-- PROJET AES GLOBAL TECH MARKET - POPULATION DE LA DIMENSION TEMPS
-- Modern Data Stack Open Source - PostgreSQL On-Premise
-- ============================================================================

CREATE OR REPLACE FUNCTION populate_dim_temps(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    current_d DATE := start_date;
    temps_id INT;
BEGIN
    WHILE current_d <= end_date LOOP
        -- Création de l'ID intelligent au format AAAAMMJJ (Ex: 20260626)
        temps_id := CAST(TO_CHAR(current_d, 'YYYYMMDD') AS INT);
        
        INSERT INTO dim_temps (
            id_temps,
            date_complete,
            annee,
            trimestre,
            mois,
            nom_mois,
            semaine_annee,
            jour_semaine,
            est_jour_ferie
        ) VALUES (
            temps_id,
            current_d,
            EXTRACT(YEAR FROM current_d),
            EXTRACT(QUARTER FROM current_d),
            EXTRACT(MONTH FROM current_d),
            -- Nom complet du mois en français
            CASE EXTRACT(MONTH FROM current_d)
                WHEN 1 THEN 'Janvier' WHEN 2 THEN 'Février' WHEN 3 THEN 'Mars'
                WHEN 4 THEN 'Avril'   WHEN 5 THEN 'Mai'      WHEN 6 THEN 'Juin'
                WHEN 7 THEN 'Juillet' WHEN 8 THEN 'Août'     WHEN 9 THEN 'Septembre'
                WHEN 10 THEN 'Octobre' WHEN 11 THEN 'Novembre' WHEN 12 THEN 'Décembre'
            END,
            EXTRACT(WEEK FROM current_d),
            -- Nom du jour de la semaine en français
            CASE EXTRACT(ISODOW FROM current_d)
                WHEN 1 THEN 'Lundi'    WHEN 2 THEN 'Mardi'    WHEN 3 THEN 'Mercredi'
                WHEN 4 THEN 'Jeudi'    WHEN 5 THEN 'Vendredi' WHEN 6 THEN 'Samedi'
                WHEN 7 THEN 'Dimanche'
            END,
            -- Identification des jours fériés génériques de la sous-région (Mali, CI, Sénégal...)
            CASE 
                -- 1er Janvier (Nouvel an)
                WHEN EXTRACT(MONTH FROM current_d) = 1 AND EXTRACT(DAY FROM current_d) = 1 THEN TRUE 
                -- 1er Mai (Fête du Travail)
                WHEN EXTRACT(MONTH FROM current_d) = 5 AND EXTRACT(DAY FROM current_d) = 1 THEN TRUE 
                -- 25 Décembre (Noël)
                WHEN EXTRACT(MONTH FROM current_d) = 12 AND EXTRACT(DAY FROM current_d) = 25 THEN TRUE
                ELSE FALSE
            END
        ) ON CONFLICT (id_temps) DO NOTHING;
        
        current_d := current_d + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Exécution de la fonction pour générer les 17 années de couverture temporelle
SELECT populate_dim_temps('2011-01-01', '2027-12-31');

-- Suppression de la fonction après initialisation pour nettoyer la base
DROP FUNCTION populate_dim_temps(DATE, DATE);