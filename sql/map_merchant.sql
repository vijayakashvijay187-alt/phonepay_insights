CREATE TABLE IF NOT EXISTS map_merchant (
    id BIGSERIAL PRIMARY KEY,
    geo_level TEXT NOT NULL,
    state TEXT,
    district TEXT,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    registered_merchants BIGINT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_map_merchant
    ON map_merchant (geo_level, COALESCE(state, ''), COALESCE(district, ''), year, quarter);

CREATE INDEX IF NOT EXISTS ix_map_merchant_lookup
    ON map_merchant (geo_level, state, year, quarter);
