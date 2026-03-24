-- Runs only on first initialization of the Postgres data directory (new volume).
-- Extra database for services/catalog in local compose overlay.
CREATE DATABASE zhuchka_catalog OWNER zhuchka;
