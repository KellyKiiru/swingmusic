"""
This file contains the SQL queries to create the database tables.
"""


CREATE_USERDATA_TABLES = """
CREATE TABLE IF NOT EXISTS playlists (
    id integer PRIMARY KEY,
    artisthashes text,
    banner_pos integer NOT NULL,
    has_gif integer,
    image text,
    last_updated text not null,
    name text not null,
    trackhashes text
);

CREATE TABLE IF NOT EXISTS favorites (
    id integer PRIMARY KEY,
    hash text not null,
    type text not null
);

CREATE TABLE IF NOT EXISTS settings (
    id integer PRIMARY KEY,
    root_dirs text NOT NULL,
    exclude_dirs text
)
"""

CREATE_APPDB_TABLES = """
CREATE TABLE IF NOT EXISTS tracks (
    id integer PRIMARY KEY,
    album text NOT NULL,
    albumartist text NOT NULL,
    albumhash text NOT NULL,
    artist text NOT NULL,
    bitrate integer NOT NULL,
    copyright text,
    date text NOT NULL,
    disc integer NOT NULL,
    duration integer NOT NULL,
    filepath text NOT NULL,
    folder text NOT NULL,
    genre text,
    title text NOT NULL,
    track integer NOT NULL,
    trackhash text NOT NULL,
    UNIQUE (filepath)
);

CREATE TABLE IF NOT EXISTS albums (
    id integer PRIMARY KEY,
    albumhash text NOT NULL,
    colors text NOT NULL,
    UNIQUE (albumhash)
);



CREATE TABLE IF NOT EXISTS artists (
    id integer PRIMARY KEY,
    artisthash text NOT NULL,
    colors text,
    bio text,
    UNIQUE (artisthash)
);

CREATE TABLE IF NOT EXISTS folders (
    id integer PRIMARY KEY,
    path text NOT NULL,
    trackcount integer NOT NULL
);
"""

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS migrations (
    id integer PRIMARY KEY,
    pre_init_version integer NOT NULL DEFAULT 0,
    post_init_version integer NOT NULL DEFAULT 0
);

INSERT INTO migrations (pre_init_version, post_init_version)
SELECT 0, 0
WHERE NOT EXISTS (SELECT 1 FROM migrations);
"""
