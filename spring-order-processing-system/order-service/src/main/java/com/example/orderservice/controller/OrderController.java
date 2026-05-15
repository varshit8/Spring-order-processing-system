package com.example.orderservice.controller;

import com.example.common.event.OrderCreatedEvent;
import com.example.orderservice.dto.OrderRequest;
import com.example.orderservice.service.OrderProducer;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderProducer producer;

    public OrderController(OrderProducer producer) {
        this.producer = producer;
    }

    @PostMapping
    public ResponseEntity<OrderCreatedEvent> createOrder(@Valid @RequestBody OrderRequest request) {
        OrderCreatedEvent event = producer.publishOrder(request.getCustomerId(), request.getTotalAmount());
        return ResponseEntity.accepted().body(event);
    }
}
