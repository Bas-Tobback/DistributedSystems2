#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE feed;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "feed" <<-EOSQL
    CREATE TABLE feed(
        username TEXT NOT NULL,
        activity TEXT NOT NULL,
        activity_time TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (username, activity_time)
    );
EOSQL