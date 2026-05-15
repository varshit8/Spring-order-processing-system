# Spring Order Processing System

A starter scaffold for a distributed, event-driven order processing backend built with Spring Boot.

## Architecture

Services:
- `order-service`
- `payment-service`
- `inventory-service`
- `notification-service`
- `analytics-service`
- `common` shared event and DTO classes

Communication:
- REST API for service entry points
- Kafka events for asynchronous workflows
- PostgreSQL for order/payment persistence
- MongoDB for analytics event storage
- Redis for distributed cache / idempotency

## Getting started

1. Navigate to the new workspace:

```powershell
cd spring-order-processing-system
```

2. Start local services with Docker Compose:

```powershell
docker compose up --build
```

3. Access sample services:
- Order service: `http://localhost:8081/api/orders`
- Payment service: `http://localhost:8082/api/payments`
- Inventory service: `http://localhost:8083/api/inventory`
- Notification service: `http://localhost:8084/api/notifications`
- Analytics service: `http://localhost:8085/api/metrics`

## Notes

- Kafka is configured with a retry-friendly topic pattern.
- Services include starter event listeners and producers for order/payment/inventory workflows.
- Kubernetes manifests are included under `k8s/`.
- CI workflow is defined in `.github/workflows/java-ci.yml`.
