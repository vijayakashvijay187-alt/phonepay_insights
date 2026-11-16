CREATE TABLE IF NOT EXISTS aggregated_transaction (
    id BIGSERIAL PRIMARY KEY,
    state TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    transaction_count BIGINT,
    transaction_amount DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_aggregated_transaction
    ON aggregated_transaction (state, year, quarter, transaction_type);

CREATE INDEX IF NOT EXISTS ix_aggregated_transaction_period
    ON aggregated_transaction (year, quarter);
