CREATE TABLE IF NOT EXISTS map_user (
    id BIGSERIAL PRIMARY KEY,
    geo_level TEXT NOT NULL,
    state TEXT,
    district TEXT,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    registered_users BIGINT,
    app_opens BIGINT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_map_user
    ON map_user (geo_level, COALESCE(state, ''), COALESCE(district, ''), year, quarter);

CREATE INDEX IF NOT EXISTS ix_map_user_lookup
    ON map_user (geo_level, state, year, quarter);
