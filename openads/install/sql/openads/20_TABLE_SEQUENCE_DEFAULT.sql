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

;

-- communes
CREATE TABLE openads.communes (
    id_communes integer NOT NULL,
    anneemajic integer,
    ccodep text,
    codcomm text,
    nom text,
    codeinsee character(5) NOT NULL,
    created_user text,
    created_date date,
    last_edited_user text,
    last_edited_date date,
    geom public.geometry(MultiPolygon,2154)
);


-- communes_id_communes_seq
CREATE SEQUENCE openads.communes_id_communes_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- communes_id_communes_seq
ALTER SEQUENCE openads.communes_id_communes_seq OWNED BY openads.communes.id_communes;


-- contraintes
CREATE TABLE openads.contraintes (
    id_contraintes integer NOT NULL,
    libelle text,
    texte text,
    groupe text,
    sous_groupe text
);


-- contraintes_id_contraintes_seq
CREATE SEQUENCE openads.contraintes_id_contraintes_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- contraintes_id_contraintes_seq
ALTER SEQUENCE openads.contraintes_id_contraintes_seq OWNED BY openads.contraintes.id_contraintes;


-- dossiers_openads
CREATE TABLE openads.dossiers_openads (
    id_dossiers_openads integer NOT NULL,
    codeinsee character(5) NOT NULL,
    numero text,
    parcelles text[],
    x double precision,
    y double precision,
    dossier_importe_geosig boolean,
    geom public.geometry(MultiPolygon,2154)
);


-- dossiers_openads_id_dossiers_openads_seq
CREATE SEQUENCE openads.dossiers_openads_id_dossiers_openads_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- dossiers_openads_id_dossiers_openads_seq
ALTER SEQUENCE openads.dossiers_openads_id_dossiers_openads_seq OWNED BY openads.dossiers_openads.id_dossiers_openads;


-- geo_contraintes
CREATE TABLE openads.geo_contraintes (
    id_geo_contraintes integer NOT NULL,
    id_contraintes integer NOT NULL,
    texte text,
    codeinsee character(5) NOT NULL,
    geom public.geometry(Polygon,2154)
);


-- geo_contraintes_id_geo_contraintes_seq
CREATE SEQUENCE openads.geo_contraintes_id_geo_contraintes_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- geo_contraintes_id_geo_contraintes_seq
ALTER SEQUENCE openads.geo_contraintes_id_geo_contraintes_seq OWNED BY openads.geo_contraintes.id_geo_contraintes;


-- parcelles
CREATE TABLE openads.parcelles (
    id_parcelles integer NOT NULL,
    ccocom text,
    ccodep text,
    ccodir text,
    ccopre text,
    ccosec text,
    dnupla text,
    ident text,
    ndeb text,
    sdeb text,
    nom text,
    type text,
    geom public.geometry(MultiPolygon,2154)
);


-- parcelles_id_parcelles_seq
CREATE SEQUENCE openads.parcelles_id_parcelles_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- parcelles_id_parcelles_seq
ALTER SEQUENCE openads.parcelles_id_parcelles_seq OWNED BY openads.parcelles.id_parcelles;


-- qgis_plugin
CREATE TABLE openads.qgis_plugin (
    id integer NOT NULL,
    version text NOT NULL,
    version_date date NOT NULL,
    status smallint NOT NULL
);


-- communes id_communes
ALTER TABLE ONLY openads.communes ALTER COLUMN id_communes SET DEFAULT nextval('openads.communes_id_communes_seq'::regclass);


-- contraintes id_contraintes
ALTER TABLE ONLY openads.contraintes ALTER COLUMN id_contraintes SET DEFAULT nextval('openads.contraintes_id_contraintes_seq'::regclass);


-- dossiers_openads id_dossiers_openads
ALTER TABLE ONLY openads.dossiers_openads ALTER COLUMN id_dossiers_openads SET DEFAULT nextval('openads.dossiers_openads_id_dossiers_openads_seq'::regclass);


-- geo_contraintes id_geo_contraintes
ALTER TABLE ONLY openads.geo_contraintes ALTER COLUMN id_geo_contraintes SET DEFAULT nextval('openads.geo_contraintes_id_geo_contraintes_seq'::regclass);


-- parcelles id_parcelles
ALTER TABLE ONLY openads.parcelles ALTER COLUMN id_parcelles SET DEFAULT nextval('openads.parcelles_id_parcelles_seq'::regclass);


--
-- PostgreSQL database dump complete
--


COMMIT;
