package domain

import "context"

type TransactionRepository interface {
	Save(ctx context.Context, tx *Transaction) error
	// Add other methods
}

type TransactionHistoryRepository interface {
	AddTransaction(ctx context.Context, userID string, amount float64, timestamp int64) error
	GetCount(ctx context.Context, userID string, startTime int64) (int64, error)
}
