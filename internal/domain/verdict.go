package domain

import (
	"time"
)

type CheckVerdict struct {
	TransactionID  string       `json:"transaction_id"`
	CorrelationID  string       `json:"correlation_id"`
	Status         string       `json:"status"` // e.g., APPROVED, SUSPICIOUS
	TriggeredRules []RuleResult `json:"triggered_rules"`
	ExecutedAt     time.Time    `json:"executed_at"`
}
