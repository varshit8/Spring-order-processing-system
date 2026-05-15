package com.example.common.event;

import java.time.Instant;

public record OrderCreatedEvent(String orderId, String customerId, double amount, Instant createdAt) {
}
