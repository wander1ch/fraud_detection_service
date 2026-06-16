package kafka

import (
	"context"
	"encoding/json"
	"log"
	"time"
	"github.com/segmentio/kafka-go"
	"github.com/sotremont/fraud_detection_service/internal/domain"
)

type Consumer struct {
	reader     *kafka.Reader
	engine     interface {
		CheckTransaction(ctx context.Context, tx *domain.Transaction) ([]domain.RuleResult, error)
	}
	txRepo     domain.TransactionRepository
	histRepo   domain.TransactionHistoryRepository
	notifier   domain.Notifier
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
	
	// Simple retry loop to handle transient "Leader Not Available" errors during startup
	for {
		msg, err := c.reader.FetchMessage(ctx)
		if err != nil {
			if err == context.Canceled {
				return
			}
			log.Printf("failed to fetch message, retrying in 2s: %v", err)
			time.Sleep(2 * time.Second)
			continue
		}
		
		log.Printf("Received message: %s", string(msg.Value))

		var tx domain.Transaction
		if err := json.Unmarshal(msg.Value, &tx); err != nil {
			log.Printf("failed to unmarshal transaction: %v", err)
			continue
		}
		log.Printf("Transaction unmarshaled: %+v", tx)

		// Analysis
		results, err := c.engine.CheckTransaction(ctx, &tx)
		if err != nil {
			log.Printf("failed to check transaction: %v", err)
			continue
		}
		log.Printf("Transaction checked, results: %+v", results)

		// Store
		_ = c.txRepo.Save(ctx, &tx)
		_ = c.histRepo.AddTransaction(ctx, tx.UserID, tx.Amount, tx.Timestamp.Unix())
		log.Println("Transaction stored and history updated")

		// Notify
		for _, res := range results {
			if res.IsFraud {
				_ = c.notifier.Send(ctx, domain.Alert{TransactionID: tx.ID, CorrelationID: tx.CorrelationID})
				log.Printf("Alert sent for transaction: %s", tx.ID)
			}
		}

		_ = c.reader.CommitMessages(ctx, msg)
		log.Println("Message committed")
	}
}
