CREATE TABLE IF NOT EXISTS aggregated_merchant (
    id BIGSERIAL PRIMARY KEY,
    state TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    registered_merchants BIGINT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_aggregated_merchant
    ON aggregated_merchant (state, year, quarter);

CREATE INDEX IF NOT EXISTS ix_aggregated_merchant_period
    ON aggregated_merchant (year, quarter);
