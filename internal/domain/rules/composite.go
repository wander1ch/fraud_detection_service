package rules

import (
	"context"
	"github.com/sotremont/fraud_detection_service/internal/domain"
	"time"
)

type CompositeRule struct {
	id      string
	name    string
	repo    domain.TransactionHistoryRepository
	limit   int64
	minutes int
}

func NewCompositeRule(id, name string, repo domain.TransactionHistoryRepository, limit int64, minutes int) *CompositeRule {
	return &CompositeRule{id: id, name: name, repo: repo, limit: limit, minutes: minutes}
}

func (r *CompositeRule) ID() string   { return r.id }
func (r *CompositeRule) Name() string { return r.name }
func (r *CompositeRule) Evaluate(ctx context.Context, tx *domain.Transaction) (domain.RuleResult, error) {
	startTime := time.Now().Add(time.Duration(-r.minutes) * time.Minute).Unix()
	count, err := r.repo.GetCount(ctx, tx.UserID, startTime)
	if err != nil {
		return domain.RuleResult{RuleID: r.id, RuleName: r.name, Error: err}, err
	}
	
	triggered := count > r.limit
	return domain.RuleResult{
		RuleID:      r.id,
		RuleName:    r.name,
		IsTriggered: triggered,
		IsFraud:     triggered,
	}, nil
}
