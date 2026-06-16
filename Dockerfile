FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o fraud-detector ./cmd/app/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/fraud-detector .
CMD ["./fraud-detector"]
