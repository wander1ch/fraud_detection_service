package rules

import (
	"context"
	"encoding/json"
	"github.com/sotremont/fraud_detection_service/internal/domain"
)

type ThresholdRule struct {
	id        string
	name      string
	currency  string
	maxAmount float64
}

func NewThresholdRule(id, name, config string) (*ThresholdRule, error) {
	var cfg struct {
		Currency   string  `json:"currency"`
		MaxAmount float64 `json:"max_amount"`
	}
	if err := json.Unmarshal([]byte(config), &cfg); err != nil {
		return nil, err
	}
	return &ThresholdRule{id: id, name: name, currency: cfg.Currency, maxAmount: cfg.MaxAmount}, nil
}

func (r *ThresholdRule) ID() string   { return r.id }
func (r *ThresholdRule) Name() string { return r.name }
func (r *ThresholdRule) Evaluate(ctx context.Context, tx *domain.Transaction) (domain.RuleResult, error) {
	triggered := tx.Currency == r.currency && tx.Amount > r.maxAmount
	return domain.RuleResult{
		RuleID:      r.id,
		RuleName:    r.name,
		IsTriggered: triggered,
		IsFraud:     triggered,
	}, nil
}
