#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE share;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "share" <<-EOSQL
    CREATE TABLE share(
        playlist_id TEXT NOT NULL,
        username TEXT NOT NULL,
        PRIMARY KEY (playlist_id, username)
    );
EOSQL