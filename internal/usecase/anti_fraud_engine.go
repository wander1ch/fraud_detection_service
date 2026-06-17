package usecase

import (
	"context"
	"sync"
	"time"

	"github.com/sotremont/fraud_detection_service/internal/domain"
	"github.com/sotremont/fraud_detection_service/internal/telemetry"
	"golang.org/x/sync/errgroup"
)

type antiFraudEngine struct {
	mu    sync.RWMutex
	rules []domain.Rule
}

func NewAntiFraudEngine() *antiFraudEngine {
	return &antiFraudEngine{rules: make([]domain.Rule, 0)}
}

func (e *antiFraudEngine) RegisterRule(rule domain.Rule) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.rules = append(e.rules, rule)
}

func (e *antiFraudEngine) CheckTransaction(ctx context.Context, tx *domain.Transaction) ([]domain.RuleResult, error) {
	e.mu.RLock()
	rules := e.rules
	e.mu.RUnlock()

	results := make([]domain.RuleResult, len(rules))
	g, gCtx := errgroup.WithContext(ctx)

	for i, rule := range rules {
		i, rule := i, rule
		g.Go(func() error {
			ctx, cancel := context.WithTimeout(gCtx, 100*time.Millisecond)
			defer cancel()
			res, err := rule.Evaluate(ctx, tx)
			if err != nil {
				return err
			}
			results[i] = res

			if res.IsTriggered {
				telemetry.RuleHits.WithLabelValues(rule.ID(), rule.Name()).Inc()
			}
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, err
	}

	for _, res := range results {
		if res.IsFraud {
			telemetry.FraudAlerts.Inc()
		}
	}

	return results, nil
}
