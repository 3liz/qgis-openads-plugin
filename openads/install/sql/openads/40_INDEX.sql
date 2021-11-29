BEGIN;
--
-- PostgreSQL database dump
--

-- Dumped from database version 13.5 (Ubuntu 13.5-2.pgdg20.04+1)
-- Dumped by pg_dump version 13.5 (Ubuntu 13.5-2.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- communes_index_geom_gist
CREATE INDEX communes_index_geom_gist ON openads.communes USING gist (geom);


-- dossiers_openads_index_geom_gist
CREATE INDEX dossiers_openads_index_geom_gist ON openads.dossiers_openads USING gist (geom);


-- geo_contraintes_id_contraintes_idx
CREATE INDEX geo_contraintes_id_contraintes_idx ON openads.geo_contraintes USING btree (id_contraintes);


-- geo_contraintes_index_geom_gist
CREATE INDEX geo_contraintes_index_geom_gist ON openads.geo_contraintes USING gist (geom);


-- parcelles_index_geom_gist
CREATE INDEX parcelles_index_geom_gist ON openads.parcelles USING gist (geom);


-- qgis_plugin_id_idx
CREATE INDEX qgis_plugin_id_idx ON openads.qgis_plugin USING btree (id);


--
-- PostgreSQL database dump complete
--


COMMIT;
