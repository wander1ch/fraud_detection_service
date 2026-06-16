package domain

import (
	"context"
)

type Alert struct {
	ID            string       `json:"id"`
	TransactionID string       `json:"transaction_id"`
	CorrelationID string       `json:"correlation_id"`
	Verdict       CheckVerdict `json:"verdict"`
}

type Notifier interface {
	Send(ctx context.Context, alert Alert) error
}
