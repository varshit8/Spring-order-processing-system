package com.example.analyticsservice.listener;

import com.example.common.event.KafkaTopics;
import com.example.common.event.OrderCreatedEvent;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class AnalyticsListener {
    private static final Logger logger = LoggerFactory.getLogger(AnalyticsListener.class);

    @KafkaListener(topics = KafkaTopics.ORDERS_CREATED, groupId = "analytics-service")
    public void captureOrderMetrics(OrderCreatedEvent event) {
        logger.info("Analytics captured order {} amount {}", event.orderId(), event.amount());
        // TODO: persist analytics data into MongoDB or a reporting store
        Instant capturedAt = Instant.now();
        logger.debug("Captured metrics for order {} at {}", event.orderId(), capturedAt);
    }
}
