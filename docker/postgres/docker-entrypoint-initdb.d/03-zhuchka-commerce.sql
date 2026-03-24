-- Runs only on first initialization of the Postgres data directory (new volume).
-- Extra database for services/commerce in local compose overlay.
CREATE DATABASE zhuchka_commerce OWNER zhuchka;
