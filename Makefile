.PHONY: up down run test lint migrate clean logs

# Infrastructure management
up:
	docker compose -f deploy/docker-compose.yaml up -d

down:
	docker compose -f deploy/docker-compose.yaml down -v

# Application execution
run:
	go run cmd/app/main.go

# Development tasks
build:
	go build -o bin/app cmd/app/main.go

test:
	go test -v ./internal/...

lint:
	golangci-lint run

migrate:
	@echo "Running migrations..."
	# Assuming a migration tool like golang-migrate is used
	# migrate -path migrations -database "${DB_URL}" up

# Utilities
logs:
	docker compose -f deploy/docker-compose.yaml logs -f app

clean:
	rm -rf bin/
