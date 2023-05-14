#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE login;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "login" <<-EOSQL
    CREATE TABLE login(
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        PRIMARY KEY (username)
    );
EOSQL
