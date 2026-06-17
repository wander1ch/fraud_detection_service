package service

import (
	"bytes"
	"context"
	"encoding/json"
	"log"
	"net/http"
	"github.com/sotremont/fraud_detection_service/internal/domain"
)

type webhookNotifier struct {
	url string
}

func NewWebhookNotifier(url string) domain.Notifier {
	return &webhookNotifier{url: url}
}

func (n *webhookNotifier) Send(ctx context.Context, alert domain.Alert) error {
	data, err := json.Marshal(alert)
	if err != nil {
		return err
	}
	log.Printf("Sending webhook to %s, body: %s", n.url, string(data)) // Добавлено логирование
	req, err := http.NewRequestWithContext(ctx, "POST", n.url, bytes.NewBuffer(data))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	log.Printf("Webhook response status: %d", resp.StatusCode)
	return nil
}
