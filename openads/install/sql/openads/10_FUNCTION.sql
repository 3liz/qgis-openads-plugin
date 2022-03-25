BEGIN;
--
-- PostgreSQL database dump
--

-- Dumped from database version 13.6 (Ubuntu 13.6-1.pgdg20.04+1)
-- Dumped by pg_dump version 13.6 (Ubuntu 13.6-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- ajout_modif_dossier()
CREATE FUNCTION openads.ajout_modif_dossier() RETURNS trigger
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


--
-- PostgreSQL database dump complete
--


COMMIT;
