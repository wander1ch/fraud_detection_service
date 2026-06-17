package kafka

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/sotremont/fraud_detection_service/internal/domain"
	"github.com/sotremont/fraud_detection_service/internal/telemetry"
)

type Consumer struct {
	reader     *kafka.Reader
	engine     interface {
		CheckTransaction(ctx context.Context, tx *domain.Transaction) ([]domain.RuleResult, error)
	}
	txRepo   domain.TransactionRepository
	histRepo domain.TransactionHistoryRepository
	notifier domain.Notifier
}

func NewConsumer(brokers []string, topic, groupID string, engine interface {
	CheckTransaction(ctx context.Context, tx *domain.Transaction) ([]domain.RuleResult, error)
}, txRepo domain.TransactionRepository, histRepo domain.TransactionHistoryRepository, notifier domain.Notifier) *Consumer {
	return &Consumer{
		reader: kafka.NewReader(kafka.ReaderConfig{
			Brokers: brokers,
			Topic:   topic,
			GroupID: groupID,
		}),
		engine:   engine,
		txRepo:   txRepo,
		histRepo: histRepo,
		notifier: notifier,
	}
}

func (c *Consumer) Start(ctx context.Context) {
	log.Println("Consumer started fetching...")

	for {
		msg, err := c.reader.FetchMessage(ctx)
		if err != nil {
			if err == context.Canceled {
				return
			}
			log.Printf("failed to fetch message, retrying in 10s: %v", err)
			time.Sleep(10 * time.Second)
			continue
		}

		start := time.Now()

		var tx domain.Transaction
		if err := json.Unmarshal(msg.Value, &tx); err != nil {
			log.Printf("failed to unmarshal transaction: %v", err)
			telemetry.TransactionsTotal.WithLabelValues("error").Inc()
			continue
		}

		// Analysis
		results, err := c.engine.CheckTransaction(ctx, &tx)
		if err != nil {
			log.Printf("failed to check transaction: %v", err)
			telemetry.TransactionsTotal.WithLabelValues("error").Inc()
			continue
		}

		telemetry.TransactionsTotal.WithLabelValues("success").Inc()
		telemetry.TransactionLatency.WithLabelValues("success").Observe(time.Since(start).Seconds())

		// Store
		_ = c.txRepo.Save(ctx, &tx)
		_ = c.histRepo.AddTransaction(ctx, tx.UserID, tx.Amount, tx.Timestamp.Unix())

		// Notify
		for _, res := range results {
			if res.IsFraud {
				if err := c.notifier.Send(ctx, domain.Alert{TransactionID: tx.ID, CorrelationID: tx.CorrelationID}); err != nil {
					log.Printf("failed to send alert for transaction %s: %v", tx.ID, err)
				} else {
					log.Printf("Alert sent successfully for transaction: %s", tx.ID)
				}
			}
		}

		_ = c.reader.CommitMessages(ctx, msg)
	}
}
