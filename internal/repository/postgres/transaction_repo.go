package postgres

import (
	"context"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/sotremont/fraud_detection_service/internal/domain"
)

type transactionRepository struct {
	db *pgxpool.Pool
}

func NewTransactionRepository(db *pgxpool.Pool) domain.TransactionRepository {
	return &transactionRepository{db: db}
}

func (r *transactionRepository) Save(ctx context.Context, tx *domain.Transaction) error {
	query := `INSERT INTO transactions (id, correlation_id, user_id, amount, currency) VALUES ($1, $2, $3, $4, $5)`
	_, err := r.db.Exec(ctx, query, tx.ID, tx.CorrelationID, tx.UserID, tx.Amount, tx.Currency)
	return err
}
