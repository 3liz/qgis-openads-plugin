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

;

-- qgis_plugin
CREATE TABLE openads.qgis_plugin (
    id integer NOT NULL,
    version text NOT NULL,
    version_date date NOT NULL,
    status smallint NOT NULL
);


--
-- PostgreSQL database dump complete
--


COMMIT;
