package rules

import (
	"context"
	"github.com/sotremont/fraud_detection_service/internal/domain"
	"sync"
)

type PatternRule struct {
	id             string
	name           string
	cardBlacklist  sync.Map
	ipBlacklist    sync.Map
}

func NewPatternRule(id, name string) *PatternRule {
	return &PatternRule{id: id, name: name}
}

func (r *PatternRule) AddCard(card string) { r.cardBlacklist.Store(card, true) }
func (r *PatternRule) AddIP(ip string)     { r.ipBlacklist.Store(ip, true) }

func (r *PatternRule) ID() string   { return r.id }
func (r *PatternRule) Name() string { return r.name }
func (r *PatternRule) Evaluate(ctx context.Context, tx *domain.Transaction) (domain.RuleResult, error) {
	_, cardBlocked := r.cardBlacklist.Load(tx.CardNumber)
	_, ipBlocked := r.ipBlacklist.Load(tx.ClientIP)
	triggered := cardBlocked || ipBlocked
	return domain.RuleResult{
		RuleID:      r.id,
		RuleName:    r.name,
		IsTriggered: triggered,
		IsFraud:     triggered,
	}, nil
}
