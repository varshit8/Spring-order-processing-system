package com.example.paymentservice.listener;

import com.example.common.event.KafkaTopics;
import com.example.common.event.OrderCreatedEvent;
import com.example.common.event.PaymentCompletedEvent;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class PaymentListener {
    private static final Logger logger = LoggerFactory.getLogger(PaymentListener.class);
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public PaymentListener(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    @KafkaListener(topics = KafkaTopics.ORDERS_CREATED, groupId = "payment-service")
    public void handleOrderCreated(OrderCreatedEvent event) {
        logger.info("Processing payment for order {}", event.orderId());
        PaymentCompletedEvent completed = new PaymentCompletedEvent(event.orderId(), true, "PAY-" + event.orderId(), Instant.now());
        kafkaTemplate.send(KafkaTopics.PAYMENTS_COMPLETED, completed);
    }
}
