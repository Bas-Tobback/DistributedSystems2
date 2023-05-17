#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlist;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlist" <<-EOSQL
    CREATE TABLE playlist(
        username TEXT NOT NULL,
        playlist TEXT NOT NULL,
        playlist_id SERIAL PRIMARY KEY
    );

    CREATE TABLE playlist_songs (
        playlist_id INT NOT NULL,
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        playlist_song_id SERIAL PRIMARY KEY
    );
EOSQL