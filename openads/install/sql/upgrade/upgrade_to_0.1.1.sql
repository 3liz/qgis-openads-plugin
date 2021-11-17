BEGIN;

-- Convert Polygon to MultiPlygon
ALTER TABLE openads.dossiers_openads ALTER COLUMN geom TYPE geometry(MultiPolygon,2154) USING ST_Multi(geom);

ALTER TABLE openads.dossiers_sig ALTER COLUMN geom TYPE geometry(MultiPolygon,2154) USING ST_Multi(geom);

COMMIT;
