package redis

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
	"github.com/sotremont/fraud_detection_service/internal/domain"
)

type historyRepository struct {
	rdb *redis.Client
}

func NewHistoryRepository(rdb *redis.Client) domain.TransactionHistoryRepository {
	return &historyRepository{rdb: rdb}
}

func (r *historyRepository) AddTransaction(ctx context.Context, userID string, amount float64, timestamp int64) error {
	key := fmt.Sprintf("user_history:%s", userID)
	return r.rdb.ZAdd(ctx, key, redis.Z{
		Score:  float64(timestamp),
		Member: fmt.Sprintf("%d:%f", timestamp, amount),
	}).Err()
}

func (r *historyRepository) GetCount(ctx context.Context, userID string, startTime int64) (int64, error) {
	key := fmt.Sprintf("user_history:%s", userID)
	return r.rdb.ZCount(ctx, key, fmt.Sprintf("%d", startTime), "+inf").Result()
}
