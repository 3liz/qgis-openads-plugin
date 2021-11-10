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

-- communes
COMMENT ON TABLE openads.communes IS 'Contient les communes';


-- contraintes
COMMENT ON TABLE openads.contraintes IS 'Permet de récupérer les contraintes par groupe';


-- dossiers_openads
COMMENT ON TABLE openads.dossiers_openads IS 'Stocke les dossiers créés automatiquement par openADS associés à une liste de parcelles, une emprise et un centroïde';


-- dossiers_sig
COMMENT ON TABLE openads.dossiers_sig IS 'Stocke les dossiers spécifiques au SIG, notamment ceux dessinés à la main par les utilisateurs';


-- geo_contraintes
COMMENT ON TABLE openads.geo_contraintes IS 'Complémentaire pour les contraintes avec la géométrie';


-- parcelles
COMMENT ON TABLE openads.parcelles IS 'Contient les parcelles';


-- qgis_plugin
COMMENT ON TABLE openads.qgis_plugin IS 'Version and date of the database structure. Useful for database structure and glossary data migrations between the plugin versions by the QGIS plugin openads';


--
-- PostgreSQL database dump complete
--


COMMIT;
