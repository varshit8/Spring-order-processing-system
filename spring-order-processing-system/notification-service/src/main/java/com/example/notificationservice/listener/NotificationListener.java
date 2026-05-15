package com.example.notificationservice.listener;

import com.example.common.event.KafkaTopics;
import com.example.common.event.OrderCreatedEvent;
import com.example.common.event.NotificationEvent;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class NotificationListener {
    private static final Logger logger = LoggerFactory.getLogger(NotificationListener.class);
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public NotificationListener(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    @KafkaListener(topics = KafkaTopics.ORDERS_CREATED, groupId = "notification-service")
    public void handleNewOrder(OrderCreatedEvent event) {
        logger.info("Sending notification for order {}", event.orderId());
        NotificationEvent notification = new NotificationEvent(event.orderId(), "Order accepted", "Your order is being processed", Instant.now());
        kafkaTemplate.send(KafkaTopics.NOTIFICATIONS_SENT, notification);
    }
}
