package main

import (
	"encoding/json"
	"fmt"
	"time"
)

type Transaction struct {
	ID            string    `json:"id"`
	CorrelationID string    `json:"correlation_id"`
	UserID        string    `json:"user_id"`
	CardNumber    string    `json:"card_number"`
	Amount        float64   `json:"amount"`
	Currency      string    `json:"currency"`
	ClientIP      string    `json:"client_ip"`
	Country       string    `json:"country"`
	Timestamp     time.Time `json:"timestamp"`
}

func main() {
	data := []byte(`{"id": "test-123", "amount": 15000, "currency": "EUR"}`)
	var tx Transaction
	err := json.Unmarshal(data, &tx)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Printf("Parsed: %+v\n", tx)
}
