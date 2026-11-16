CREATE TABLE IF NOT EXISTS aggregated_user (
    id BIGSERIAL PRIMARY KEY,
    state TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    row_kind TEXT NOT NULL,
    brand TEXT,
    registered_users BIGINT,
    app_opens BIGINT,
    device_count BIGINT,
    device_percentage DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_aggregated_user
    ON aggregated_user (state, year, quarter, row_kind, COALESCE(brand, ''));

CREATE INDEX IF NOT EXISTS ix_aggregated_user_period
    ON aggregated_user (year, quarter);
