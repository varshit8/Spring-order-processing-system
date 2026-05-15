package com.example.inventoryservice.listener;

import com.example.common.event.KafkaTopics;
import com.example.common.event.OrderCreatedEvent;
import com.example.common.event.InventoryReservedEvent;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class InventoryListener {
    private static final Logger logger = LoggerFactory.getLogger(InventoryListener.class);
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public InventoryListener(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    @KafkaListener(topics = KafkaTopics.ORDERS_CREATED, groupId = "inventory-service")
    public void reserveInventory(OrderCreatedEvent event) {
        logger.info("Reserving inventory for order {}", event.orderId());
        InventoryReservedEvent reserved = new InventoryReservedEvent(event.orderId(), true, Instant.now());
        kafkaTemplate.send(KafkaTopics.INVENTORY_RESERVED, reserved);
    }
}
