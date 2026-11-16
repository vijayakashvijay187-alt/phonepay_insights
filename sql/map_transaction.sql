CREATE TABLE IF NOT EXISTS map_transaction (
    id BIGSERIAL PRIMARY KEY,
    geo_level TEXT NOT NULL,
    state TEXT,
    district TEXT,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    transaction_count BIGINT,
    transaction_amount DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_map_transaction
    ON map_transaction (geo_level, COALESCE(state, ''), COALESCE(district, ''), year, quarter);

CREATE INDEX IF NOT EXISTS ix_map_transaction_lookup
    ON map_transaction (geo_level, state, year, quarter);
