package main

import (
	"context"
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
	"go.uber.org/zap"
	"net/http"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()

	// Metrics
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		logger.Info("Starting metrics server on :9090")
		if err := http.ListenAndServe(":9090", nil); err != nil {
			logger.Error("metrics server failed", zap.Error(err))
		}
	}()

	// 1. DB
	db, err := pgxpool.New(ctx, os.Getenv("DB_URL"))
	if err != nil {
		logger.Fatal("failed to connect to db", zap.Error(err))
	}
	defer db.Close()

	// 2. Redis
	rdb := goredis.NewClient(&goredis.Options{Addr: os.Getenv("REDIS_URL")})
	defer rdb.Close()

	// 3. Engine & Rules
	engine := usecase.NewAntiFraudEngine()
	
	// Threshold Rule
	tRule, _ := rules.NewThresholdRule("rule1", "EUR_Limit", `{"currency":"EUR", "max_amount":10000}`)
	engine.RegisterRule(tRule)

	// Repos
	txRepo := postgres.NewTransactionRepository(db)
	histRepo := redisrepo.NewHistoryRepository(rdb)
	notifier := service.NewWebhookNotifier("http://mock-webhook:8080")

	// 4. Kafka Consumer
	brokers := []string{os.Getenv("KAFKA_BROKERS")}
	consumer := kafka.NewConsumer(
		brokers,
		"transactions",
		"fraud-group",
		engine, txRepo, histRepo, notifier,
	)

	logger.Info("Service started. Listening to Kafka...")
	consumer.Start(ctx)
}
