CREATE TABLE IF NOT EXISTS top_merchant (
    id BIGSERIAL PRIMARY KEY,
    scope_state TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    entity_level TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    registered_merchants BIGINT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_top_merchant
    ON top_merchant (scope_state, year, quarter, entity_level, entity_name);

CREATE INDEX IF NOT EXISTS ix_top_merchant_lookup
    ON top_merchant (scope_state, year, quarter, entity_level);
