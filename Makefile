.PHONY: run build test lint migrate

run:
	go run cmd/app/main.go

build:
	go build -o bin/app cmd/app/main.go

test:
	go test -v ./...

lint:
	golangci-lint run

migrate:
	# Add migration tool command here
	echo "Running migrations..."
