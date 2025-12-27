#!/usr/bin/env python3
"""
Performance Regression Testing Suite for Chat Loop System.

Tests the performance optimizations implemented in Phase 3:
- Incremental memory management
- Performance monitoring
- Memory efficiency
- Tool execution optimization

This suite ensures that performance improvements are maintained
and can detect regressions in future changes.
"""

from src.core.chat_loop import ChatLoop

import unittest
import time
import gc
import psutil
import os
from unittest.mock import MagicMock, patch

# Add src to path for testing
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class PerformanceRegressionTestCase(unittest.TestCase):
    """Base class for performance regression tests with common setup."""

    def setUp(self):
        """Set up test environment with memory tracking."""
        self.chat_loop = ChatLoop()
        self.mock_ctx = MagicMock()
        self.mock_ctx.conversation_history = []
        self.mock_ctx.context_mode = "off"

        # Mock config with reasonable values
        self.mock_config = MagicMock()
        self.mock_config.max_history_pairs = 50  # Higher for testing
        self.chat_loop.config = self.mock_config
        self.chat_loop.ctx = self.mock_ctx

        # Performance baselines
        self.baseline_memory_usage = self._get_memory_usage()
        self.performance_baselines = {
            "input_validation_max_time": 0.001,  # 1ms
            "memory_trim_max_time": 0.01,  # 10ms
            "performance_monitoring_max_time": 0.001,  # 1ms
        }

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def _assert_performance_within_baseline(
        self, operation_name: str, operation_func, max_time: float, iterations: int = 1
    ):
        """Assert that an operation performs within baseline time."""
        times = []
        for _ in range(iterations):
            start_time = time.time()
            operation_func()
            elapsed = time.time() - start_time
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time_measured = max(times)

        self.assertLessEqual(
            avg_time,
            max_time,
            f"{operation_name} average time {avg_time:.4f}s exceeds baseline {max_time}s",
        )

        return avg_time, max_time_measured

    def _assert_memory_efficiency(
        self, operation_name: str, operation_func, max_memory_increase: float = 5.0
    ):
        """Assert that an operation doesn't increase memory usage significantly."""
        gc.collect()  # Clean up before measurement
        memory_before = self._get_memory_usage()

        operation_func()

        gc.collect()  # Clean up after measurement
        memory_after = self._get_memory_usage()

        memory_increase = memory_after - memory_before

        self.assertLessEqual(
            memory_increase,
            max_memory_increase,
            f"{operation_name} memory increase {memory_increase:.2f}MB exceeds threshold {max_memory_increase}MB",
        )

        return memory_increase


class TestInputValidationPerformance(PerformanceRegressionTestCase):
    """Test performance of input validation operations."""

    def test_input_validation_performance(self):
        """Test that input validation meets performance baseline."""
        test_inputs = [
            "short",
            "medium length input for testing performance",
            "very long input " * 100,  # ~2800 chars
            f"unicode test: {chr(128512)} {chr(129299)}",  # Emojis
            "special chars: !@#$%^&*()[]{}|\\:;\"'<>,.?/",
        ]

        for test_input in test_inputs:

            def validate_input():
                try:
                    self.chat_loop._validate_input(test_input)
                except Exception:
                    pass  # Expected for some invalid inputs

            avg_time, max_time = self._assert_performance_within_baseline(
                f"input_validation_{len(test_input)}_chars",
                validate_input,
                self.performance_baselines["input_validation_max_time"],
                iterations=5,
            )

            print(
                f"✅ Input validation {len(test_input)} chars: avg={avg_time:.4f}s, max={max_time:.4f}s"
            )

    def test_content_sanitization_performance(self):
        """Test that content sanitization meets performance baseline."""
        test_contents = [
            "clean content",
            "content with\ncontrol\tchars",
            "content with " + "\x00" * 100 + " embedded nulls",
            "unicode heavy content: " + "🚀" * 1000,
            "mixed content:\n\r\t\x01\x02\x03clean\x04\x05",
        ]

        for test_content in test_contents:

            def sanitize_content():
                self.chat_loop._sanitize_content(test_content)

            avg_time, max_time = self._assert_performance_within_baseline(
                f"content_sanitization_{len(test_content)}_chars",
                sanitize_content,
                self.performance_baselines["input_validation_max_time"],
                iterations=5,
            )

            print(
                f"✅ Content sanitization {len(test_content)} chars: avg={avg_time:.4f}s, max={max_time:.4f}s"
            )

    def test_empty_input_validation_performance(self):
        """Test performance of empty input validation."""

        def validate_empty():
            try:
                self.chat_loop._validate_input("")
            except Exception:
                pass

        avg_time, max_time = self._assert_performance_within_baseline(
            "empty_input_validation",
            validate_empty,
            self.performance_baselines["input_validation_max_time"],
            iterations=10,
        )

        print(f"✅ Empty input validation: avg={avg_time:.4f}s, max={max_time:.4f}s")


class TestMemoryManagementPerformance(PerformanceRegressionTestCase):
    """Test performance of memory management operations."""

    def test_memory_trimming_performance(self):
        """Test that memory trimming operations meet performance baseline."""
        # Add many messages to trigger trimming
        threshold = (self.chat_loop.config.max_history_pairs * 2 + 5) * 1.5

        for i in range(int(threshold) + 50):
            self.mock_ctx.conversation_history.append(f"memory_test_message_{i}")

        def trim_memory():
            self.chat_loop._trim_conversation_history_incremental()

        avg_time, max_time = self._assert_performance_within_baseline(
            "memory_trimming_large_dataset",
            trim_memory,
            self.performance_baselines["memory_trim_max_time"],
            iterations=3,
        )

        print(
            f"✅ Memory trimming large dataset: avg={avg_time:.4f}s, max={max_time:.4f}s"
        )

    def test_memory_threshold_detection_performance(self):
        """Test that memory threshold detection is efficient."""
        threshold = (self.chat_loop.config.max_history_pairs * 2 + 5) * 1.5

        # Add messages up to threshold
        for i in range(int(threshold) + 20):
            self.mock_ctx.conversation_history.append(f"threshold_test_{i}")

        def check_threshold():
            return self.chat_loop._should_trim_memory()

        avg_time, max_time = self._assert_performance_within_baseline(
            "memory_threshold_detection",
            check_threshold,
            self.performance_baselines["input_validation_max_time"],
            iterations=100,
        )

        print(
            f"✅ Memory threshold detection: avg={avg_time:.6f}s, max={max_time:.6f}s"
        )

    def test_memory_efficiency_during_tool_execution(self):
        """Test that tool execution with memory management is memory efficient."""
        # Add many messages to trigger memory management
        threshold = (self.chat_loop.config.max_history_pairs * 2 + 5) * 1.5

        for i in range(int(threshold) + 30):
            self.mock_ctx.conversation_history.append(f"tool_test_{i}")

        with patch("src.core.chat_loop.ToolRegistry") as mock_registry_class:
            mock_registry_instance = mock_registry_class.return_value
            mock_registry_instance.execute.return_value = {
                "success": True,
                "result": "test",
            }

            tool_call = {"name": "test_tool", "args": {}}

            def execute_tool_with_memory():
                self.chat_loop._execute_single_tool(tool_call)

            # Test memory efficiency
            memory_increase = self._assert_memory_efficiency(
                "tool_execution_with_memory_management",
                execute_tool_with_memory,
                max_memory_increase=2.0,  # 2MB threshold
            )

            print(f"✅ Tool execution memory increase: {memory_increase:.2f}MB")

    def test_conversation_history_persistence_performance(self):
        """Test that conversation history operations are efficient."""
        # Add test messages
        test_messages = [f"persistence_test_{i}" for i in range(100)]
        self.mock_ctx.conversation_history.extend(test_messages)

        def test_history_operations():
            # Test history length
            length = len(self.mock_ctx.conversation_history)

            # Test history trimming
            from src.storage.memory import trim_history

            trimmed = trim_history(self.mock_ctx.conversation_history, 50)

            # Test history append
            self.mock_ctx.conversation_history.append("new_message")

            return length, len(trimmed)

        avg_time, max_time = self._assert_performance_within_baseline(
            "conversation_history_operations",
            test_history_operations,
            self.performance_baselines["input_validation_max_time"],
            iterations=10,
        )

        print(
            f"✅ Conversation history operations: avg={avg_time:.4f}s, max={max_time:.4f}s"
        )


class TestPerformanceMonitoringPerformance(PerformanceRegressionTestCase):
    """Test performance of performance monitoring system."""

    def test_performance_monitoring_overhead(self):
        """Test that performance monitoring doesn't add significant overhead."""

        def dummy_operation():
            time.sleep(0.001)  # 1ms operation

        # Test monitoring overhead
        start_time = time.time()
        for _ in range(100):
            op_start = time.time()
            dummy_operation()
            self.chat_loop._monitor_performance("test_operation", op_start)
        total_time = time.time() - start_time

        # Should complete in reasonable time
        self.assertLess(total_time, 1.0, "Performance monitoring overhead too high")

        print(
            f"✅ Performance monitoring overhead: {total_time:.4f}s for 100 operations"
        )

    def test_performance_stats_gathering_performance(self):
        """Test that performance stats gathering is efficient."""
        # Add some test data
        self.mock_ctx.conversation_history.extend(
            [f"stats_test_{i}" for i in range(20)]
        )

        def gather_stats():
            return self.chat_loop._get_performance_stats()

        avg_time, max_time = self._assert_performance_within_baseline(
            "performance_stats_gathering",
            gather_stats,
            self.performance_baselines["performance_monitoring_max_time"],
            iterations=100,
        )

        print(
            f"✅ Performance stats gathering: avg={avg_time:.6f}s, max={max_time:.6f}s"
        )

    def test_adaptive_logging_performance(self):
        """Test that adaptive logging levels work efficiently."""
        # Test different operation times
        test_cases = [
            ("fast_op", 0.0001),  # Fast operation
            ("medium_op", 0.5),  # Medium operation
            ("slow_op", 6.0),  # Slow operation
        ]

        for op_name, duration in test_cases:

            def timed_operation():
                start = time.time() - duration
                self.chat_loop._monitor_performance(op_name, start)

            avg_time, max_time = self._assert_performance_within_baseline(
                f"adaptive_logging_{op_name}",
                timed_operation,
                self.performance_baselines["performance_monitoring_max_time"],
                iterations=10,
            )

            print(
                f"✅ Adaptive logging {op_name}: avg={avg_time:.6f}s, max={max_time:.6f}s"
            )


class TestIntegratedPerformance(PerformanceRegressionTestCase):
    """Test integrated performance of complete workflows."""

    def test_complete_iteration_performance(self):
        """Test performance of complete chat iteration."""
        # Mock all dependencies
        with (
            patch("src.core.chat_loop.get_context") as mock_get_ctx,
            patch("src.core.chat_loop.ToolRegistry.execute") as mock_execute,
            patch("src.core.chat_loop.save_memory"),
            patch("src.core.context_utils.get_relevant_context", return_value=""),
        ):
            mock_ctx = MagicMock()
            mock_ctx.conversation_history = []
            mock_ctx.context_mode = "off"
            mock_get_ctx.return_value = mock_ctx
            mock_execute.return_value = {"success": True, "result": "test"}

            mock_llm = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm

            # Simple response without tools
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.tool_calls = []
            mock_llm.invoke.return_value = mock_response

            mock_ctx.llm = mock_llm

            # Test complete iteration
            def run_complete_iteration():
                return self.chat_loop.run_iteration("test input")

            avg_time, max_time = self._assert_performance_within_baseline(
                "complete_iteration",
                run_complete_iteration,
                max_time=0.1,  # 100ms for complete iteration
                iterations=5,
            )

            print(f"✅ Complete iteration: avg={avg_time:.4f}s, max={max_time:.4f}s")

    def test_multi_tool_iteration_performance(self):
        """Test performance of iteration with multiple tool calls."""
        # Mock LLM with tool calls
        with (
            patch("src.core.chat_loop.get_context") as mock_get_ctx,
            patch("src.core.chat_loop.ToolRegistry.execute") as mock_execute,
            patch("src.core.chat_loop.save_memory"),
            patch("src.core.context_utils.get_relevant_context", return_value=""),
        ):
            mock_ctx = MagicMock()
            mock_ctx.conversation_history = []
            mock_ctx.context_mode = "off"
            mock_get_ctx.return_value = mock_ctx

            mock_llm = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm

            # Response with tool calls
            tool_call = {"name": "test_tool", "args": {}, "id": "123"}
            mock_response = MagicMock()
            mock_response.content = "Calling tool"
            mock_response.tool_calls = [tool_call]

            # Final response
            final_response = MagicMock()
            final_response.content = "Tool result processed"
            final_response.tool_calls = []

            mock_llm.invoke.side_effect = [mock_response, final_response]
            mock_ctx.llm = mock_llm

            mock_execute.return_value = {
                "success": True,
                "result": "tool_output",
            }

            def run_multi_tool_iteration():
                return self.chat_loop.run_iteration("call test tool")

            avg_time, max_time = self._assert_performance_within_baseline(
                "multi_tool_iteration",
                run_multi_tool_iteration,
                max_time=0.2,  # 200ms for multi-tool iteration
                iterations=3,
            )

            print(f"✅ Multi-tool iteration: avg={avg_time:.4f}s, max={max_time:.4f}s")


class TestPerformanceRegressionMonitoring(unittest.TestCase):
    """Monitor performance regressions over time."""

    def test_performance_baseline_estishment(self):
        """Establish performance baselines for regression monitoring."""
        chat_loop = ChatLoop()
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = []
        mock_ctx.context_mode = "off"
        mock_config = MagicMock()
        mock_config.max_history_pairs = 50
        chat_loop.config = mock_config
        chat_loop.ctx = mock_ctx

        # Run performance tests and establish baselines
        baselines = {}

        # Input validation baseline
        start_time = time.time()
        for _ in range(100):
            try:
                chat_loop._validate_input("test input")
            except Exception:
                pass
        baselines["input_validation_100_ops"] = time.time() - start_time

        # Memory management baseline
        for i in range(200):
            mock_ctx.conversation_history.append(f"baseline_test_{i}")

        start_time = time.time()
        for _ in range(10):
            chat_loop._trim_conversation_history_incremental()
        baselines["memory_trim_10_ops"] = time.time() - start_time

        # Save baselines to file for future regression testing
        import json

        with open("performance_baselines.json", "w") as f:
            json.dump(baselines, f, indent=2)

        print("📊 Performance baselines established:")
        for test_name, time_taken in baselines.items():
            print(f"  {test_name}: {time_taken:.4f}s")

        # Verify baselines are reasonable
        self.assertLess(
            baselines["input_validation_100_ops"],
            0.1,
            "Input validation baseline too slow",
        )
        self.assertLess(
            baselines["memory_trim_10_ops"], 0.1, "Memory trimming baseline too slow"
        )


def run_performance_regression_suite():
    """Run the complete performance regression test suite."""
    print("🚀 PERFORMANCE REGRESSION TEST SUITE")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestInputValidationPerformance,
        TestMemoryManagementPerformance,
        TestPerformanceMonitoringPerformance,
        TestIntegratedPerformance,
        TestPerformanceRegressionMonitoring,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE REGRESSION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\n❌ PERFORMANCE REGRESSION DETECTED:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\n💥 TEST ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.split('Exception:')[-1].strip()}")

    if not result.failures and not result.errors:
        print("\n🎉 ALL PERFORMANCE TESTS PASSED!")
        print("✅ No performance regressions detected")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_performance_regression_suite()
