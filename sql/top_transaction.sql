CREATE TABLE IF NOT EXISTS top_transaction (
    id BIGSERIAL PRIMARY KEY,
    scope_state TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    entity_level TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    transaction_count BIGINT,
    transaction_amount DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_top_transaction
    ON top_transaction (scope_state, year, quarter, entity_level, entity_name);

CREATE INDEX IF NOT EXISTS ix_top_transaction_lookup
    ON top_transaction (scope_state, year, quarter, entity_level);
