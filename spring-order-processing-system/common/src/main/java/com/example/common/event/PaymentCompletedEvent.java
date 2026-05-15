package com.example.common.event;

import java.time.Instant;

public record PaymentCompletedEvent(String orderId, boolean success, String paymentReference, Instant processedAt) {
}
