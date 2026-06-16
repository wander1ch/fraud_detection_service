package rules

import (
	"context"
	"testing"
	"github.com/sotremont/fraud_detection_service/internal/domain"
)

func TestThresholdRule_Evaluate(t *testing.T) {
	rule, err := NewThresholdRule("test-rule", "Test Rule", `{"currency":"EUR", "max_amount":1000}`)
	if err != nil {
		t.Fatalf("failed to create rule: %v", err)
	}

	tests := []struct {
		name      string
		tx        *domain.Transaction
		wantFraud bool
	}{
		{
			name:      "Under limit",
			tx:        &domain.Transaction{Amount: 500, Currency: "EUR"},
			wantFraud: false,
		},
		{
			name:      "Exactly limit",
			tx:        &domain.Transaction{Amount: 1000, Currency: "EUR"},
			wantFraud: false,
		},
		{
			name:      "Over limit",
			tx:        &domain.Transaction{Amount: 1001, Currency: "EUR"},
			wantFraud: true,
		},
		{
			name:      "Different currency",
			tx:        &domain.Transaction{Amount: 2000, Currency: "USD"},
			wantFraud: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			res, err := rule.Evaluate(context.Background(), tt.tx)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if res.IsFraud != tt.wantFraud {
				t.Errorf("IsFraud = %v, want %v", res.IsFraud, tt.wantFraud)
			}
		})
	}
}
