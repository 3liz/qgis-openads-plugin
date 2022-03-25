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

-- dossiers_openads trg_add_update_dossier_openads
CREATE TRIGGER trg_add_update_dossier_openads BEFORE INSERT OR UPDATE ON openads.dossiers_openads FOR EACH ROW EXECUTE PROCEDURE openads.ajout_modif_dossier();


--
-- PostgreSQL database dump complete
--


COMMIT;
