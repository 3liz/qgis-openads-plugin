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

SET default_tablespace = '';

-- communes communes_codeinsee_unique
ALTER TABLE ONLY openads.communes
    ADD CONSTRAINT communes_codeinsee_unique UNIQUE (codeinsee);


-- communes communes_pkey
ALTER TABLE ONLY openads.communes
    ADD CONSTRAINT communes_pkey PRIMARY KEY (id_communes);


-- contraintes contraintes_pkey
ALTER TABLE ONLY openads.contraintes
    ADD CONSTRAINT contraintes_pkey PRIMARY KEY (id_contraintes);


-- dossiers_openads dossiers_openads_numero_unique
ALTER TABLE ONLY openads.dossiers_openads
    ADD CONSTRAINT dossiers_openads_numero_unique UNIQUE (numero);


-- dossiers_openads dossiers_openads_pkey
ALTER TABLE ONLY openads.dossiers_openads
    ADD CONSTRAINT dossiers_openads_pkey PRIMARY KEY (id_dossiers_openads);


-- geo_contraintes geo_contraintes_pkey
ALTER TABLE ONLY openads.geo_contraintes
    ADD CONSTRAINT geo_contraintes_pkey PRIMARY KEY (id_geo_contraintes);


-- parcelles parcelles_ident_unique
ALTER TABLE ONLY openads.parcelles
    ADD CONSTRAINT parcelles_ident_unique UNIQUE (ident);


-- parcelles parcelles_pkey
ALTER TABLE ONLY openads.parcelles
    ADD CONSTRAINT parcelles_pkey PRIMARY KEY (id_parcelles);


-- qgis_plugin qgis_plugin_pkey
ALTER TABLE ONLY openads.qgis_plugin
    ADD CONSTRAINT qgis_plugin_pkey PRIMARY KEY (id);


-- geo_contraintes geo_contraintes_fkey
ALTER TABLE ONLY openads.geo_contraintes
    ADD CONSTRAINT geo_contraintes_fkey FOREIGN KEY (id_contraintes) REFERENCES openads.contraintes(id_contraintes) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


COMMIT;
