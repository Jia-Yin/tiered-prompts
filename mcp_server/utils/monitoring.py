#!/usr/bin/env python3
"""
Monitoring and Metrics Collection for MCP Server

This module provides comprehensive monitoring, logging, and performance metrics
for the MCP server operations.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from functools import wraps
import traceback

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for MCP operations"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = float('inf')

    # Tool-specific metrics
    tool_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Resource metrics
    resource_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Recent response times (for calculating moving averages)
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))

    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recent_errors: List[Dict[str, Any]] = field(default_factory=list)

class MCPMonitor:
    """Comprehensive monitoring for MCP server operations"""

    def __init__(self, max_recent_errors: int = 50):
        self.metrics = PerformanceMetrics()
        self.max_recent_errors = max_recent_errors
        self.start_time = datetime.now()
        self._lock = threading.Lock()

        # Setup logger
        self.logger = logging.getLogger(f"{__name__}.MCPMonitor")
        self._setup_logging()

    def _setup_logging(self):
        """Setup structured logging for MCP operations"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler for MCP operations
        try:
            file_handler = logging.FileHandler('mcp_server.log')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Could not setup file logging: {e}")

    def log_request(self, operation_type: str, operation_name: str,
                   parameters: Dict[str, Any], user_id: str = None):
        """Log incoming MCP request"""
        self.logger.info(
            f"MCP Request - Type: {operation_type}, Name: {operation_name}, "
            f"Params: {json.dumps(parameters, default=str)[:200]}..."
        )

    def log_response(self, operation_type: str, operation_name: str,
                    success: bool, response_time: float,
                    error_message: str = None):
        """Log MCP response"""
        status = "SUCCESS" if success else "FAILED"
        log_level = logging.INFO if success else logging.ERROR

        message = (
            f"MCP Response - Type: {operation_type}, Name: {operation_name}, "
            f"Status: {status}, Time: {response_time:.3f}s"
        )

        if error_message:
            message += f", Error: {error_message}"

        self.logger.log(log_level, message)

    def record_operation(self, operation_type: str, operation_name: str,
                        response_time: float, success: bool,
                        error_message: str = None):
        """Record operation metrics"""
        with self._lock:
            # Update general metrics
            self.metrics.total_requests += 1
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1

            # Update response time metrics
            self.metrics.recent_response_times.append(response_time)
            if response_time > self.metrics.max_response_time:
                self.metrics.max_response_time = response_time
            if response_time < self.metrics.min_response_time:
                self.metrics.min_response_time = response_time

            # Calculate average response time
            if self.metrics.recent_response_times:
                self.metrics.average_response_time = sum(
                    self.metrics.recent_response_times
                ) / len(self.metrics.recent_response_times)

            # Update operation-specific metrics
            metrics_dict = (
                self.metrics.tool_metrics if operation_type == "tool"
                else self.metrics.resource_metrics
            )

            if operation_name not in metrics_dict:
                metrics_dict[operation_name] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "avg_response_time": 0.0,
                    "max_response_time": 0.0,
                    "recent_times": deque(maxlen=20)
                }

            op_metrics = metrics_dict[operation_name]
            op_metrics["total_calls"] += 1
            op_metrics["recent_times"].append(response_time)

            if success:
                op_metrics["successful_calls"] += 1
            else:
                op_metrics["failed_calls"] += 1

            if response_time > op_metrics["max_response_time"]:
                op_metrics["max_response_time"] = response_time

            if op_metrics["recent_times"]:
                op_metrics["avg_response_time"] = sum(
                    op_metrics["recent_times"]
                ) / len(op_metrics["recent_times"])

            # Record errors
            if not success and error_message:
                self.metrics.error_counts[error_message] += 1
                self.metrics.recent_errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "operation_type": operation_type,
                    "operation_name": operation_name,
                    "error_message": error_message,
                    "response_time": response_time
                })

                # Keep recent errors list manageable
                if len(self.metrics.recent_errors) > self.max_recent_errors:
                    self.metrics.recent_errors = self.metrics.recent_errors[-self.max_recent_errors:]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self._lock:
            uptime = datetime.now() - self.start_time

            return {
                "system_info": {
                    "uptime_seconds": uptime.total_seconds(),
                    "uptime_formatted": str(uptime),
                    "start_time": self.start_time.isoformat()
                },
                "request_metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "success_rate": (
                        self.metrics.successful_requests / self.metrics.total_requests * 100
                        if self.metrics.total_requests > 0 else 0
                    )
                },
                "performance_metrics": {
                    "average_response_time": self.metrics.average_response_time,
                    "max_response_time": self.metrics.max_response_time,
                    "min_response_time": (
                        self.metrics.min_response_time
                        if self.metrics.min_response_time != float('inf') else 0
                    )
                },
                "tool_metrics": dict(self.metrics.tool_metrics),
                "resource_metrics": dict(self.metrics.resource_metrics),
                "error_summary": {
                    "total_errors": self.metrics.failed_requests,
                    "error_types": dict(self.metrics.error_counts),
                    "recent_errors": self.metrics.recent_errors[-10:]  # Last 10 errors
                }
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        with self._lock:
            success_rate = (
                self.metrics.successful_requests / self.metrics.total_requests * 100
                if self.metrics.total_requests > 0 else 100
            )

            avg_response_time = self.metrics.average_response_time

            # Determine health status
            if success_rate >= 95 and avg_response_time <= 1.0:
                status = "healthy"
            elif success_rate >= 90 and avg_response_time <= 2.0:
                status = "warning"
            else:
                status = "critical"

            return {
                "status": status,
                "success_rate": success_rate,
                "average_response_time": avg_response_time,
                "total_requests": self.metrics.total_requests,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            }

# ============================================================================
# DECORATORS FOR MONITORING
# ============================================================================

def monitor_mcp_operation(monitor: MCPMonitor, operation_type: str):
    """Decorator to monitor MCP operations"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            operation_name = func.__name__
            start_time = time.time()

            # Log request
            monitor.log_request(operation_type, operation_name, kwargs)

            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time

                # Log successful response
                monitor.log_response(operation_type, operation_name, True, response_time)
                monitor.record_operation(operation_type, operation_name, response_time, True)

                return result

            except Exception as e:
                response_time = time.time() - start_time
                error_message = str(e)

                # Log failed response
                monitor.log_response(operation_type, operation_name, False, response_time, error_message)
                monitor.record_operation(operation_type, operation_name, response_time, False, error_message)

                # Log full traceback for debugging
                monitor.logger.error(f"Exception in {operation_name}: {traceback.format_exc()}")

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            operation_name = func.__name__
            start_time = time.time()

            # Log request
            monitor.log_request(operation_type, operation_name, kwargs)

            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time

                # Log successful response
                monitor.log_response(operation_type, operation_name, True, response_time)
                monitor.record_operation(operation_type, operation_name, response_time, True)

                return result

            except Exception as e:
                response_time = time.time() - start_time
                error_message = str(e)

                # Log failed response
                monitor.log_response(operation_type, operation_name, False, response_time, error_message)
                monitor.record_operation(operation_type, operation_name, response_time, False, error_message)

                # Log full traceback for debugging
                monitor.logger.error(f"Exception in {operation_name}: {traceback.format_exc()}")

                raise

        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# Global monitor instance
mcp_monitor = MCPMonitor()
