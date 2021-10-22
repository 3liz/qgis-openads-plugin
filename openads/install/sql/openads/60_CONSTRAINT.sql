BEGIN;
--
-- PostgreSQL database dump
--

-- Dumped from database version 13.4 (Ubuntu 13.4-4.pgdg21.04+1)
-- Dumped by pg_dump version 13.4 (Ubuntu 13.4-4.pgdg21.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- communes communes_pkey
ALTER TABLE ONLY openads.communes
    ADD CONSTRAINT communes_pkey PRIMARY KEY (id_communes);


-- geo_contraintes geo_contraintes_pkey
ALTER TABLE ONLY openads.geo_contraintes
    ADD CONSTRAINT geo_contraintes_pkey PRIMARY KEY (id_geo_contraintes);


-- contraintes contraintes_pkey
ALTER TABLE ONLY openads.contraintes
    ADD CONSTRAINT contraintes_pkey PRIMARY KEY (id_contraintes);


-- dossiers_openads dossiers_openads_pkey
ALTER TABLE ONLY openads.dossiers_openads
    ADD CONSTRAINT dossiers_openads_pkey PRIMARY KEY (id_dossiers_openads);


-- dossiers_sig dossiers_sig_pkey
ALTER TABLE ONLY openads.dossiers_sig
    ADD CONSTRAINT dossiers_sig_pkey PRIMARY KEY (id_dossiers_sig);


-- parcelles parcelles_pkey
ALTER TABLE ONLY openads.parcelles
    ADD CONSTRAINT parcelles_pkey PRIMARY KEY (id_parcelles);


-- geo_contraintes geo_contraintes_fkey
ALTER TABLE ONLY openads.geo_contraintes
    ADD CONSTRAINT geo_contraintes_fkey FOREIGN KEY (id_contraintes) REFERENCES openads.contraintes(id_contraintes);

-- communes communes_codeinsee_unique
ALTER TABLE ONLY openads.communes
    ADD CONSTRAINT communes_codeinsee_unique UNIQUE (codeinsee);


-- parcelles parcelles_ident_unique
ALTER TABLE ONLY openads.parcelles
    ADD CONSTRAINT parcelles_ident_unique UNIQUE (ident);


-- parcelles dossiers_sig_numero_unique
ALTER TABLE ONLY openads.dossiers_sig
    ADD CONSTRAINT dossiers_sig_numero_unique UNIQUE (numero);


-- parcelles dossiers_openads_numero_unique
ALTER TABLE ONLY openads.dossiers_openads
    ADD CONSTRAINT dossiers_openads_numero_unique UNIQUE (numero);


--
-- PostgreSQL database dump complete
--


COMMIT;
