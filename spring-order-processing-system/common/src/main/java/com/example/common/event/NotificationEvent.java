package com.example.common.event;

import java.time.Instant;

public record NotificationEvent(String orderId, String subject, String body, Instant sentAt) {
}
