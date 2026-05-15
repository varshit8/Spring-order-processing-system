# Spring Order Processing System

A distributed, event-driven order processing platform built with **Spring Boot 3.2.0**, **Apache Kafka**, and a microservices architecture. This system demonstrates asynchronous event-driven workflows for order creation, payment processing, inventory management, notifications, and analytics.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Dependencies & Libraries](#dependencies--libraries)
6. [Installation & Setup](#installation--setup)
7. [Build & Run Commands](#build--run-commands)
8. [API Endpoints](#api-endpoints)
9. [Event Flow](#event-flow)
10. [Database Configuration](#database-configuration)

---

## 🎯 Project Overview

### Functionality

The Spring Order Processing System enables:

- **Order Creation**: REST API to submit new customer orders
- **Event-Driven Workflows**: Orders trigger automatic payment processing, inventory reservation, and notifications
- **Service Decoupling**: Each service operates independently via Kafka message brokers
- **Distributed Tracing**: Centralized event logging and metrics collection
- **Scalability**: Microservices architecture allows independent scaling

### Key Features

- ✅ Multi-module Maven project (7 modules)
- ✅ Spring Boot 3.2.0 with Java 17
- ✅ Apache Kafka for event streaming
- ✅ Docker & Docker Compose for containerization
- ✅ Kubernetes manifests for cloud deployment
- ✅ H2 in-memory database for local development
- ✅ GitHub Actions CI/CD workflow
- ✅ Spring Actuator for metrics & health checks

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT (HTTP)                           │
└─────────────┬───────────────────────────────────────────────────┘
              │ POST /api/orders
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ORDER SERVICE (8080)                        │
│  • REST Controller (OrderController)                             │
│  • Order Producer (Kafka)                                        │
│  • H2 Database (in-memory)                                       │
└──────────────┬──────────────────────────────────────────────────┘
               │ Publish: orders.created event
               ▼
     ┌─────────────────────────────┐
     │  KAFKA MESSAGE BROKER       │
     │ (Topic: orders.created)     │
     └──────┬──────────┬──────┬───┘
            │          │      │
    ┌───────▼──┐  ┌────▼─┐ ┌─▼──────────────┐
    │ PAYMENT  │  │INVEN-│ │ NOTIFICATION  │
    │ SERVICE  │  │TORY  │ │ SERVICE       │
    │ (8081)   │  │SER.  │ │ (8083)        │
    │ ⬇️       │  │(8082)│ │ ⬇️             │
    │Consume   │  │⬇️    │ │Consume &      │
    │→Process  │  │Cons. │ │→Send Email/SMS│
    │→Publish  │  │→Pub. │ │               │
    │payments. │  │inven-│ │               │
    │completed │  │tory. │ │               │
    │          │  │reserved
    └────┬─────┘  └──┬──┘ └────────────────┘
         │           │
         │           └─────────────────┐
         │                             │
         ▼                             ▼
    ┌──────────────────────────────────────────┐
    │  ANALYTICS SERVICE (8084)                │
    │  • MongoDB storage                       │
    │  • Metrics aggregation                   │
    │  • Event archival                        │
    │  GET /api/metrics - View metrics         │
    └──────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### System Requirements

- **Java**: 17 or higher
- **Maven**: 3.9.9 or higher
- **Docker**: (Optional, for running Kafka/databases)
- **Git**: For version control

### Installation Links

- [Java 17 Download](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html)
- [Maven 3.9.9 Download](https://maven.apache.org/download.cgi)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

## 📁 Project Structure

```
spring-order-processing-system/
├── pom.xml                                 # Parent POM (multi-module Maven)
├── docker-compose.yml                      # Docker services configuration
├── README.md                               # This file
├── .gitignore                              # Git ignore rules
│
├── common/                                 # Shared module
│   ├── pom.xml
│   └── src/main/java/com/example/common/
│       ├── config/
│       │   └── KafkaConfig.java           # Kafka producer/consumer beans
│       └── event/
│           ├── KafkaTopics.java           # Topic names (constants)
│           ├── OrderCreatedEvent.java     # Order event schema
│           ├── PaymentCompletedEvent.java # Payment event schema
│           ├── InventoryReservedEvent.java# Inventory event schema
│           └── NotificationEvent.java     # Notification event schema
│
├── order-service/                          # Order creation service
│   ├── pom.xml
│   ├── Dockerfile
│   ├── src/main/
│   │   ├── java/com/example/orderservice/
│   │   │   ├── OrderServiceApplication.java
│   │   │   ├── controller/
│   │   │   │   └── OrderController.java    # POST /api/orders
│   │   │   ├── dto/
│   │   │   │   └── OrderRequest.java
│   │   │   └── service/
│   │   │       └── OrderProducer.java      # Publishes to Kafka
│   │   └── resources/
│   │       └── application.yml             # Configuration
│   └── target/                             # Build output
│
├── payment-service/                        # Payment processing service
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/
│       ├── java/com/example/paymentservice/
│       │   ├── PaymentServiceApplication.java
│       │   └── listener/
│       │       └── PaymentListener.java    # Consumes orders.created
│       └── resources/
│           └── application.yml
│
├── inventory-service/                      # Inventory management service
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/
│       ├── java/com/example/inventoryservice/
│       │   ├── InventoryServiceApplication.java
│       │   └── listener/
│       │       └── InventoryListener.java  # Consumes orders.created
│       └── resources/
│           └── application.yml
│
├── notification-service/                   # Notification delivery service
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/
│       ├── java/com/example/notificationservice/
│       │   ├── NotificationServiceApplication.java
│       │   └── listener/
│       │       └── NotificationListener.java# Consumes orders.created
│       └── resources/
│           └── application.yml
│
├── analytics-service/                      # Analytics & metrics service
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/
│       ├── java/com/example/analyticsservice/
│       │   ├── AnalyticsServiceApplication.java
│       │   ├── controller/
│       │   │   └── MetricsController.java  # GET /api/metrics
│       │   └── listener/
│       │       └── AnalyticsListener.java  # Listens to all events
│       └── resources/
│           └── application.yml
│
├── k8s/                                    # Kubernetes manifests
│   ├── README.md
│   ├── order-service-deployment.yaml
│   └── payment-service-deployment.yaml
│
└── .github/
    └── workflows/
        └── java-ci.yml                     # GitHub Actions CI pipeline
```

---

## 📚 Dependencies & Libraries

### Core Dependencies (managed by Spring Boot 3.2.0)

| Library | Version | Purpose |
|---------|---------|---------|
| **Spring Framework** | 6.1.1 | Core framework |
| **Spring Boot** | 3.2.0 | Boot framework & auto-configuration |
| **Spring Web** | 6.1.1 | REST controller support |
| **Spring Data JPA** | 3.2.0 | Database ORM |
| **Spring Kafka** | 3.0.11 | Kafka integration |
| **Spring Actuator** | 3.2.0 | Health checks & metrics |
| **Hibernate** | 6.3.1.Final | JPA implementation |
| **Jackson** | 2.15.2 | JSON serialization |

### Database & Storage

| Library | Version | Purpose |
|---------|---------|---------|
| **H2 Database** | 2.1.214 | In-memory DB (local dev) |
| **PostgreSQL JDBC** | 42.6.0 | PostgreSQL driver |
| **Spring Data Redis** | 3.2.0 | Redis caching |
| **Lettuce** | 6.3.0.RELEASE | Redis client |
| **MongoDB Driver** | 4.11.1 | MongoDB integration |

### Message Broker & Streaming

| Library | Version | Purpose |
|---------|---------|---------|
| **Apache Kafka Client** | 3.5.1 | Kafka producer/consumer |
| **Kafka Streams** | 3.5.1 | Stream processing |
| **Confluent Schema Registry** | (optional) | Schema management |

### Testing & Build Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **JUnit 5** | 5.9.1 | Unit testing |
| **Maven Compiler Plugin** | 3.13.0 | Java compilation |
| **Maven Surefire Plugin** | 3.2.5 | Test execution |
| **Spring Boot Maven Plugin** | 3.2.0 | Building executable JARs |

### Validation & Utilities

| Library | Version | Purpose |
|---------|---------|---------|
| **Jakarta Bean Validation** | 3.0.2 | Input validation |
| **Log4j2** | 2.20.0 | Logging framework |
| **SLF4J** | 2.0.7 | Logging facade |

---

## 🚀 Installation & Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/varshit8/Spring-order-processing-system.git
cd spring-order-processing-system
```

### Step 2: Install Maven (if not already installed)

**Windows:**
```powershell
# Download from: https://maven.apache.org/download.cgi
# Extract to: C:\Users\<username>\AppData\Local\Programs\apache-maven\apache-maven-3.9.9
# Add to PATH and verify:
mvn -v
```

**macOS/Linux:**
```bash
brew install maven
# or
sudo apt-get install maven
mvn -v
```

### Step 3: Verify Java Installation

```bash
java -version
# Expected: Java 17 or higher
```

### Step 4: Build the Project

```bash
# Install all modules to local Maven repository
mvn clean install -DskipTests
```

---

## 🏃 Build & Run Commands

### Option A: Local Development (H2 Database)

```bash
# 1. Build all modules
mvn clean package -DskipTests

# 2. Start order-service only (no Kafka dependency)
cd order-service
mvn spring-boot:run

# Access: http://localhost:8080
```

### Option B: Full Stack with Docker Compose

```bash
# 1. Build Docker images
docker compose build

# 2. Start all services
docker compose up

# Services will be available at:
# - Order Service: http://localhost:8081
# - Payment Service: http://localhost:8082
# - Inventory Service: http://localhost:8083
# - Notification Service: http://localhost:8084
# - Analytics Service: http://localhost:8085
# - Kafka UI: http://localhost:8080 (if included)
```

### Option C: Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check pod status
kubectl get pods
kubectl get svc

# Port forward to access services
kubectl port-forward svc/order-service 8080:8080
```

### Individual Service Commands

```bash
# Build specific module
mvn clean package -f order-service/pom.xml -DskipTests

# Run specific service
cd payment-service && mvn spring-boot:run

# Run tests
mvn clean test

# Generate project reports
mvn site

# View dependencies
mvn dependency:tree
```

---

## 🔌 API Endpoints

### Order Service (Port: 8080)

**Create Order (Triggers Event Flow)**
```http
POST /api/orders
Content-Type: application/json

{
  "customerId": "CUST-123",
  "totalAmount": 99.99
}

Response:
{
  "orderId": "ORD-001",
  "customerId": "CUST-123",
  "totalAmount": 99.99,
  "timestamp": "2026-05-15T00:36:33.000Z",
  "status": "CREATED"
}
```

**Health Check**
```http
GET /actuator/health
Response: {"status": "UP"}
```

**Metrics (if Analytics Service running)**
```http
GET /actuator/metrics
```

### Analytics Service (Port: 8084)

**Get Aggregated Metrics**
```http
GET /api/metrics
Response: {
  "totalOrders": 42,
  "totalRevenue": 4299.58,
  "averageOrderValue": 102.37,
  "paymentsProcessed": 40,
  "inventoryReserved": 42,
  "notificationsSent": 42
}
```

---

## 🔄 Event Flow (End-to-End)

### Scenario: Customer Places an Order

```
1. CLIENT → POST /api/orders
   {
     "customerId": "CUST-123",
     "totalAmount": 99.99
   }

2. ORDER-SERVICE
   ├─ Creates order record in H2/PostgreSQL
   ├─ Generates OrderCreatedEvent
   └─ Publishes to Kafka topic: orders.created

3. KAFKA MESSAGE BROKER (Topic: orders.created)
   │
   ├─→ PAYMENT-SERVICE consumes
   │   ├─ Processes payment (mock)
   │   ├─ Publishes PaymentCompletedEvent
   │   └─ Topic: payments.completed
   │
   ├─→ INVENTORY-SERVICE consumes
   │   ├─ Reserves inventory
   │   ├─ Publishes InventoryReservedEvent
   │   └─ Topic: inventory.reserved
   │
   └─→ NOTIFICATION-SERVICE consumes
       ├─ Sends email/SMS to customer
       ├─ Publishes NotificationEvent
       └─ Topic: notifications.sent

4. ANALYTICS-SERVICE
   ├─ Listens to all topics (orders.created, payments.completed, etc.)
   ├─ Stores events in MongoDB
   ├─ Aggregates metrics
   └─ Provides /api/metrics endpoint

5. MONITORING
   ├─ Each service exposes /actuator/health
   ├─ Metrics available at /actuator/metrics
   └─ CI pipeline runs on every commit (.github/workflows/java-ci.yml)
```

---

## 🗄️ Database Configuration

### Local Development (H2)

**File:** `order-service/src/main/resources/application.yml`

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driverClassName: org.h2.Driver
    username: sa
  jpa:
    database-platform: org.hibernate.dialect.H2Dialect
    hibernate:
      ddl-auto: validate
  h2:
    console:
      enabled: true
```

**Access H2 Console:** http://localhost:8080/h2-console

### Production (PostgreSQL)

**File:** `application-docker.yml`

```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/orders
    username: postgres
    password: postgres
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
```

### Analytics Storage (MongoDB)

**Configuration:**
```yaml
spring:
  data:
    mongodb:
      uri: mongodb://localhost:27017/analytics
      database: analytics
```

---

## 📊 Monitoring & Observability

### Spring Actuator Endpoints

```
GET /actuator/health              # Service health status
GET /actuator/metrics             # All available metrics
GET /actuator/metrics/jvm.memory  # JVM memory metrics
GET /actuator/metrics/http.server.requests  # HTTP request metrics
GET /actuator/prometheus          # Prometheus-compatible metrics
```

### Kafka Topic Monitoring

```bash
# List all Kafka topics
kafka-topics --list --bootstrap-server localhost:9092

# View topic details
kafka-topics --describe --topic orders.created --bootstrap-server localhost:9092

# Monitor message flow
kafka-console-consumer --topic orders.created --bootstrap-server localhost:9092 --from-beginning
```

---

## 🔐 Security Considerations

- Store sensitive data (API keys, DB passwords) in `.env` files
- Use Spring Security for authentication in production
- Enable TLS/SSL for inter-service communication
- Implement API rate limiting
- Use Spring Cloud Config for externalized configuration
- Scan dependencies: `mvn dependency-check:check`

---

## 📝 Development Workflow

### Local Testing

```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=OrderControllerTest

# Run with code coverage
mvn jacoco:report
# Report: target/site/jacoco/index.html
```

### Code Quality

```bash
# Format code
mvn spotless:apply

# Static analysis
mvn sonar:sonar

# Dependency vulnerability check
mvn org.owasp:dependency-check-maven:check
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/your-feature`
4. Open Pull Request on GitHub

---

## 📄 License

This project is licensed under the **MIT License** - see LICENSE file for details.

---

## 📞 Support & Resources

- **Spring Boot Docs:** https://spring.io/projects/spring-boot
- **Apache Kafka:** https://kafka.apache.org/
- **Docker Docs:** https://docs.docker.com/
- **Kubernetes Docs:** https://kubernetes.io/docs/

---

## 🎉 Project Created

**Date:** May 15, 2026  
**Stack:** Java 17 | Spring Boot 3.2.0 | Apache Kafka | Microservices  
**Repository:** https://github.com/varshit8/Spring-order-processing-system
