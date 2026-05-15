package com.example.analyticsservice.controller;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/metrics")
public class MetricsController {
    @GetMapping
    public Map<String, Object> health() {
        return Map.of(
                "service", "analytics-service",
                "status", "ready",
                "eventsConsumed", 0);
    }
}
