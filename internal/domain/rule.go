package domain

import (
	"context"
)

type RuleResult struct {
	RuleID      string `json:"rule_id"`
	RuleName    string `json:"rule_name"`
	IsTriggered bool   `json:"is_triggered"`
	IsFraud     bool   `json:"is_fraud"`
	Error       error  `json:"-"`
}

type Rule interface {
	ID() string
	Name() string
	Evaluate(ctx context.Context, tx *Transaction) (RuleResult, error)
}
