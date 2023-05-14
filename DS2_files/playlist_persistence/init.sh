#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlist;

EOSQL

# TODO : make new table
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlist" <<-EOSQL
    CREATE TABLE playlist(
        username TEXT NOT NULL,
        playlist TEXT NOT NULL,
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        PRIMARY KEY (username, playlist, artist, title)
    );
EOSQL