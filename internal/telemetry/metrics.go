package telemetry

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	TransactionsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "fraud_detector_transactions_total",
			Help: "Total number of processed transactions",
		},
		[]string{"status"},
	)

	TransactionLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "fraud_detector_transaction_duration_seconds",
			Help:    "Latency of transaction processing",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"status"},
	)

	RuleHits = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "fraud_detector_rule_hits_total",
			Help: "Total number of times a rule was hit",
		},
		[]string{"rule_id", "rule_name"},
	)

	FraudAlerts = promauto.NewCounter(
		prometheus.CounterOpts{
			Name: "fraud_detector_fraud_alerts_total",
			Help: "Total number of fraud alerts sent",
		},
	)
)
