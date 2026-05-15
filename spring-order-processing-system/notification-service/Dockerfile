FROM maven:3.10.1-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY pom.xml ./
COPY common/pom.xml ./common/
COPY order-service/pom.xml ./order-service/
COPY payment-service/pom.xml ./payment-service/
COPY inventory-service/pom.xml ./inventory-service/
COPY notification-service/pom.xml ./notification-service/
COPY analytics-service/pom.xml ./analytics-service/
COPY common ./common
COPY notification-service ./notification-service
RUN mvn -B -pl notification-service -am clean package -DskipTests

FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app
COPY --from=builder /workspace/notification-service/target/notification-service-0.1.0.jar ./app.jar
EXPOSE 8084
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
