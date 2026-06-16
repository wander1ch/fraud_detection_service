package domain

import (
	"time"
)

type Transaction struct {
	ID            string    `json:"id"`
	CorrelationID string    `json:"correlation_id"`
	UserID        string    `json:"user_id"`
	CardNumber    string    `json:"card_number"`
	Amount        float64   `json:"amount"`
	Currency      string    `json:"currency"`
	ClientIP      string    `json:"client_ip"`
	Country       string    `json:"country"`
	Timestamp     time.Time `json:"timestamp"`
}
