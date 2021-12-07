BEGIN;

-- Convert Polygon to MultiPolygon
ALTER TABLE openads.dossiers_openads ALTER COLUMN geom TYPE geometry(MultiPolygon,2154) USING ST_Multi(geom);

DROP TABLE IF EXISTS openads.dossiers_sig;

ALTER TABLE ONLY openads.qgis_plugin ADD CONSTRAINT qgis_plugin_pkey PRIMARY KEY (id);

-- Update geom from parcelles
CREATE OR REPLACE FUNCTION openads.ajout_modif_dossier() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    record_dossier record;
BEGIN
    SELECT INTO record_dossier
        ARRAY_AGG("id_parcelles"::text) AS parcelles_id,
        ST_Union(geom) AS geom
    FROM openads.parcelles
    WHERE "ident" = ANY (NEW.parcelles);
    IF record_dossier.geom IS NOT NULL AND cardinality(record_dossier.parcelles_id) = cardinality(NEW.parcelles) THEN
        RAISE NOTICE 'Insertion ou mise à jour dun dossier openads avec toutes les parcelles dans la base de données';
        NEW.geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(record_dossier.geom), 3));
        NEW.x = ST_X(ST_PointOnSurface(NEW.geom));
        NEW.y = ST_Y(ST_PointOnSurface(NEW.geom));
    ELSE
        RAISE NOTICE 'Insertion ou mise à jour dun dossier openads mais toutes les parcelles ne sont pas dans la base de données';
        -- do nothing on geometry
        NEW.x = NULL;
        NEW.y = NULL;
    END IF;

RETURN NEW;
END;
$$;

CREATE TRIGGER trg_add_update_dossier_openads
BEFORE INSERT OR UPDATE ON openads.dossiers_openads
FOR EACH ROW EXECUTE PROCEDURE openads.ajout_modif_dossier();

COMMENT ON FUNCTION openads.ajout_modif_dossier()
    IS 'Trigger pour l''ajout ou la modification d''un dossier pour la génération de la géométrie';

COMMIT;
