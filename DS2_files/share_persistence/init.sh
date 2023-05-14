#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE share;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "share" <<-EOSQL
    CREATE TABLE share(
        username TEXT NOT NULL,
        friend TEXT NOT NULL,
        playlist TEXT NOT NULL,
        PRIMARY KEY (username, friend, playlist)
    );
EOSQL