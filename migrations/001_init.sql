CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    correlation_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_correlation_id ON transactions(correlation_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
