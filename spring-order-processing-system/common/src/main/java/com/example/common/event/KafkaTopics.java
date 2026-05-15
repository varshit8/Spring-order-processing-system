package com.example.common.event;

public final class KafkaTopics {
    private KafkaTopics() {
    }

    public static final String ORDERS_CREATED = "orders.created";
    public static final String PAYMENTS_COMPLETED = "payments.completed";
    public static final String INVENTORY_RESERVED = "inventory.reserved";
    public static final String NOTIFICATIONS_SENT = "notifications.sent";
}
