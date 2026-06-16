package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/jackc/pgx/v5/pgxpool"
	goredis "github.com/redis/go-redis/v9"
	"github.com/sotremont/fraud_detection_service/internal/domain/rules"
	"github.com/sotremont/fraud_detection_service/internal/repository/postgres"
	redisrepo "github.com/sotremont/fraud_detection_service/internal/repository/redis"
	"github.com/sotremont/fraud_detection_service/internal/service"
	"github.com/sotremont/fraud_detection_service/internal/transport/kafka"
	"github.com/sotremont/fraud_detection_service/internal/usecase"
)

func main() {
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()

	// 1. DB
	db, err := pgxpool.New(ctx, os.Getenv("DB_URL"))
	if err != nil {
		log.Fatalf("failed to connect to db: %v", err)
	}
	defer db.Close()

	// 2. Redis
	rdb := goredis.NewClient(&goredis.Options{Addr: os.Getenv("REDIS_URL")})

	// 3. Engine & Rules
	engine := usecase.NewAntiFraudEngine()
	
	// Threshold Rule
	tRule, _ := rules.NewThresholdRule("rule1", "EUR_Limit", `{"currency":"EUR", "max_amount":10000}`)
	engine.RegisterRule(tRule)

	// Repos
	txRepo := postgres.NewTransactionRepository(db)
	histRepo := redisrepo.NewHistoryRepository(rdb)
	notifier := service.NewWebhookNotifier("https://webhook.site/cd4c65cd-36bd-48ff-a25c-83d32e4b3c9f")

	// 4. Kafka Consumer
	brokers := []string{os.Getenv("KAFKA_BROKERS")}
	consumer := kafka.NewConsumer(
		brokers,
		"transactions",
		"fraud-group",
		engine, txRepo, histRepo, notifier,
	)

	log.Println("Service started. Listening to Kafka...")
	consumer.Start(ctx)
}
