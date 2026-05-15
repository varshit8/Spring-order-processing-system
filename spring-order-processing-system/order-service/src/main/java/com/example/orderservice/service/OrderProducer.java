package com.example.orderservice.service;

import com.example.common.event.KafkaTopics;
import com.example.common.event.OrderCreatedEvent;
import java.time.Instant;
import java.util.UUID;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class OrderProducer {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public OrderProducer(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public OrderCreatedEvent publishOrder(String customerId, double amount) {
        OrderCreatedEvent event = new OrderCreatedEvent(UUID.randomUUID().toString(), customerId, amount, Instant.now());
        kafkaTemplate.send(KafkaTopics.ORDERS_CREATED, event);
        return event;
    }
}
