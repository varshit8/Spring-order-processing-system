package com.example.common.event;

import java.time.Instant;

public record InventoryReservedEvent(String orderId, boolean reserved, Instant reservedAt) {
}
