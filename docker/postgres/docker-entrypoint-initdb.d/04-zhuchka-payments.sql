-- Runs only on first initialization of the Postgres data directory (new volume).
-- Extra database for services/payments in local compose overlay.
CREATE DATABASE zhuchka_payments OWNER zhuchka;
