#!/usr/bin/env python3
"""
Performance Benchmarking Automation Suite for Chat Loop System.

Provides automated performance benchmarking, regression detection,
and performance reporting for production monitoring.
"""

from src.storage.memory import trim_history
from src.core.chat_loop import ChatLoop

import json
import time
import psutil
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""

    name: str
    duration: float
    memory_usage: float
    operations_per_second: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PerformanceBenchmark:
    """Automated performance benchmarking system."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize benchmark system."""
        self.config = self._load_config(config_path)
        self.results: List[BenchmarkResult] = []
        self.baseline_path = Path("performance_baselines.json")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load benchmark configuration."""
        default_config = {
            "thresholds": {
                "max_response_time": 5.0,  # 5 seconds
                "max_memory_growth": 50.0,  # 50MB
                "min_operations_per_second": 10.0,  # 10 ops/sec
                "max_memory_usage": 100.0,  # 100MB
            },
            "test_parameters": {
                "input_sizes": [10, 100, 1000, 10000],
                "tool_counts": [1, 5, 10, 20],
                "conversation_lengths": [10, 50, 100, 500],
                "iterations": 100,
            },
            "reporting": {
                "output_format": "json",
                "save_baseline": True,
                "compare_baseline": True,
                "alert_on_regression": True,
            },
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def run_input_validation_benchmark(self) -> BenchmarkResult:
        """Benchmark input validation performance."""
        print("🧪 Running input validation benchmark...")

        chat_loop = ChatLoop()
        test_inputs = [
            "short",
            "medium length input for testing performance",
            "very long input " * 100,
            f"unicode test: {chr(128512)} {chr(129299)}",
        ]

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        successful_operations = 0
        for _ in range(self.config["test_parameters"]["iterations"]):
            for test_input in test_inputs:
                try:
                    chat_loop._validate_input(test_input)
                    successful_operations += 1
                except Exception:
                    pass  # Expected for some invalid inputs

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        memory_growth = end_memory - start_memory
        ops_per_second = successful_operations / duration

        success = (
            duration < self.config["thresholds"]["max_response_time"]
            and memory_growth < self.config["thresholds"]["max_memory_growth"]
            and ops_per_second > self.config["thresholds"]["min_operations_per_second"]
        )

        result = BenchmarkResult(
            name="input_validation",
            duration=duration,
            memory_usage=memory_growth,
            operations_per_second=ops_per_second,
            success=success,
            metadata={
                "iterations": self.config["test_parameters"]["iterations"],
                "input_sizes": [len(inp) for inp in test_inputs],
                "successful_operations": successful_operations,
            },
        )

        print(
            f"✅ Input validation: {ops_per_second:.1f} ops/sec, {memory_growth:.2f}MB growth"
        )
        return result

    def run_memory_management_benchmark(self) -> BenchmarkResult:
        """Benchmark memory management performance."""
        print("💾 Running memory management benchmark...")

        chat_loop = ChatLoop()
        mock_ctx = chat_loop.ctx

        # Fill conversation history
        conversation_length = self.config["test_parameters"]["conversation_lengths"][
            -1
        ]  # 500
        for i in range(conversation_length):
            mock_ctx.conversation_history.append(f"memory_test_{i}")

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Perform memory management
        trimming_count = 0
        for _ in range(10):  # 10 memory management cycles
            trimmed = chat_loop._trim_conversation_history_incremental()
            if trimmed:
                trimming_count += 1

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        memory_growth = end_memory - start_memory
        ops_per_second = trimming_count / duration if duration > 0 else 0

        success = (
            duration < self.config["thresholds"]["max_response_time"]
            and memory_growth < self.config["thresholds"]["max_memory_growth"]
        )

        result = BenchmarkResult(
            name="memory_management",
            duration=duration,
            memory_usage=memory_growth,
            operations_per_second=ops_per_second,
            success=success,
            metadata={
                "conversation_length": conversation_length,
                "trimming_operations": trimming_count,
                "memory_efficiency": memory_growth / conversation_length,
            },
        )

        print(
            f"✅ Memory management: {ops_per_second:.1f} trims/sec, {memory_growth:.2f}MB growth"
        )
        return result

    def run_tool_execution_benchmark(self) -> BenchmarkResult:
        """Benchmark tool execution performance."""
        print("🔧 Running tool execution benchmark...")

        chat_loop = ChatLoop()
        mock_ctx = chat_loop.ctx

        # Add some conversation history
        for i in range(50):
            mock_ctx.conversation_history.append(f"tool_test_{i}")

        from unittest.mock import patch

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        successful_executions = 0

        with patch("src.core.chat_loop.ToolRegistry") as mock_registry:
            mock_registry.execute.return_value = {"success": True, "result": "test"}

            tool_call = {"name": "test_tool", "args": {}}

            for _ in range(self.config["test_parameters"]["iterations"]):
                try:
                    result = chat_loop._execute_single_tool(tool_call)
                    if result.get("success"):
                        successful_executions += 1
                except Exception:
                    pass

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        memory_growth = end_memory - start_memory
        ops_per_second = successful_executions / duration if duration > 0 else 0

        success = (
            duration < self.config["thresholds"]["max_response_time"]
            and memory_growth < self.config["thresholds"]["max_memory_growth"]
        )

        result = BenchmarkResult(
            name="tool_execution",
            duration=duration,
            memory_usage=memory_growth,
            operations_per_second=ops_per_second,
            success=success,
            metadata={
                "successful_executions": successful_executions,
                "iterations": self.config["test_parameters"]["iterations"],
            },
        )

        print(
            f"✅ Tool execution: {ops_per_second:.1f} execs/sec, {memory_growth:.2f}MB growth"
        )
        return result

    def run_performance_monitoring_benchmark(self) -> BenchmarkResult:
        """Benchmark performance monitoring overhead."""
        print("📊 Running performance monitoring benchmark...")

        chat_loop = ChatLoop()

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Monitor many operations
        for i in range(self.config["test_parameters"]["iterations"]):
            operation_start = time.time() - (i % 10) * 0.001  # Vary timing
            chat_loop._monitor_performance(f"benchmark_operation_{i}", operation_start)

            # Collect stats
            if i % 10 == 0:
                _ = (
                    chat_loop._get_performance_stats()
                )  # Call to get stats (not stored to avoid unused variable

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        memory_growth = end_memory - start_memory
        ops_per_second = self.config["test_parameters"]["iterations"] / duration

        success = (
            duration < self.config["thresholds"]["max_response_time"]
            and memory_growth < self.config["thresholds"]["max_memory_growth"]
        )

        result = BenchmarkResult(
            name="performance_monitoring",
            duration=duration,
            memory_usage=memory_growth,
            operations_per_second=ops_per_second,
            success=success,
            metadata={
                "monitored_operations": self.config["test_parameters"]["iterations"],
                "overhead_per_operation": duration
                / self.config["test_parameters"]["iterations"],
            },
        )

        print(
            f"✅ Performance monitoring: {ops_per_second:.1f} monitors/sec, {memory_growth:.2f}MB growth"
        )
        return result

    def run_complete_iteration_benchmark(self) -> BenchmarkResult:
        """Benchmark complete chat iteration."""
        print("🔄 Running complete iteration benchmark...")

        chat_loop = ChatLoop()
        mock_ctx = chat_loop.ctx
        mock_ctx.conversation_history = []
        mock_ctx.context_mode = "off"

        from unittest.mock import patch

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        successful_iterations = 0

        with (
            patch("src.core.chat_loop.get_context") as mock_get_ctx,
            patch("src.core.chat_loop.ToolRegistry") as mock_registry,
            patch("src.core.chat_loop.save_memory"),
            patch("src.core.context_utils.get_relevant_context", return_value=""),
        ):
            mock_get_ctx.return_value = mock_ctx

            mock_llm = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm

            # Simple response without tools
            mock_response = MagicMock()
            mock_response.content = "Benchmark response"
            mock_response.tool_calls = []
            mock_llm.invoke.return_value = mock_response

            mock_ctx.llm = mock_llm

            for _ in range(
                min(10, self.config["test_parameters"]["iterations"])
            ):  # Fewer iterations for complete test
                try:
                    response = chat_loop.run_iteration("benchmark input")
                    if response:
                        successful_iterations += 1
                except Exception:
                    pass

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        memory_growth = end_memory - start_memory
        ops_per_second = successful_iterations / duration if duration > 0 else 0

        success = (
            duration < self.config["thresholds"]["max_response_time"]
            and memory_growth < self.config["thresholds"]["max_memory_growth"]
        )

        result = BenchmarkResult(
            name="complete_iteration",
            duration=duration,
            memory_usage=memory_growth,
            operations_per_second=ops_per_second,
            success=success,
            metadata={
                "successful_iterations": successful_iterations,
                "iterations": min(10, self.config["test_parameters"]["iterations"]),
            },
        )

        print(
            f"✅ Complete iteration: {ops_per_second:.1f} iters/sec, {memory_growth:.2f}MB growth"
        )
        return result

    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmark tests."""
        print("🚀 Starting Performance Benchmark Suite")
        print("=" * 50)

        benchmarks = [
            self.run_input_validation_benchmark,
            self.run_memory_management_benchmark,
            self.run_tool_execution_benchmark,
            self.run_performance_monitoring_benchmark,
            self.run_complete_iteration_benchmark,
        ]

        results = []
        for benchmark in benchmarks:
            try:
                result = benchmark()
                results.append(result)
                if not result.success:
                    print(f"❌ {result.name} benchmark failed!")
            except Exception as e:
                print(f"💥 {benchmark.__name__} crashed: {e}")
                results.append(
                    BenchmarkResult(
                        name=benchmark.__name__,
                        duration=0,
                        memory_usage=0,
                        operations_per_second=0,
                        success=False,
                        error_message=str(e),
                    )
                )

        return results

    def save_baseline(self, results: List[BenchmarkResult]):
        """Save benchmark results as baseline."""
        if not self.config["reporting"]["save_baseline"]:
            return

        baseline = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total
                / 1024
                / 1024
                / 1024,  # GB
                "python_version": sys.version,
            },
            "results": [
                {
                    "name": r.name,
                    "duration": r.duration,
                    "memory_usage": r.memory_usage,
                    "operations_per_second": r.operations_per_second,
                    "metadata": r.metadata,
                }
                for r in results
            ],
        }

        with open(self.baseline_path, "w") as f:
            json.dump(baseline, f, indent=2)

        print(f"📊 Baseline saved to {self.baseline_path}")

    def compare_with_baseline(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Compare current results with baseline."""
        if (
            not self.config["reporting"]["compare_baseline"]
            or not self.baseline_path.exists()
        ):
            return {}

        with open(self.baseline_path, "r") as f:
            baseline = json.load(f)

        comparison = {
            "timestamp": datetime.now().isoformat(),
            "baseline_timestamp": baseline["timestamp"],
            "regressions": [],
            "improvements": [],
            "summary": {},
        }

        current_results = {r.name: r for r in results}

        for baseline_result in baseline["results"]:
            name = baseline_result["name"]
            if name not in current_results:
                continue

            current = current_results[name]
            baseline_duration = baseline_result["duration"]
            baseline_memory = baseline_result["memory_usage"]
            baseline_ops = baseline_result["operations_per_second"]

            # Calculate regressions/improvements
            duration_change = (
                (current.duration - baseline_duration) / baseline_duration * 100
            )
            memory_change = (
                (current.memory_usage - baseline_memory) / baseline_memory * 100
                if baseline_memory > 0
                else 0
            )
            ops_change = (
                (current.operations_per_second - baseline_ops) / baseline_ops * 100
                if baseline_ops > 0
                else 0
            )

            if duration_change > 10 or memory_change > 10 or ops_change < -10:
                comparison["regressions"].append(
                    {
                        "name": name,
                        "duration_change": duration_change,
                        "memory_change": memory_change,
                        "ops_change": ops_change,
                    }
                )
            elif duration_change < -5 or memory_change < -5 or ops_change > 10:
                comparison["improvements"].append(
                    {
                        "name": name,
                        "duration_change": duration_change,
                        "memory_change": memory_change,
                        "ops_change": ops_change,
                    }
                )

        return comparison

    def generate_report(
        self, results: List[BenchmarkResult], comparison: Dict[str, Any]
    ) -> str:
        """Generate benchmark report."""
        report = []
        report.append("# Performance Benchmark Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)

        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        report.append(f"## Summary")
        report.append(f"- Tests Run: {total_tests}")
        report.append(f"- Tests Passed: {passed_tests}")
        report.append(f"- Success Rate: {passed_tests / total_tests * 100:.1f}%")

        # Individual results
        report.append("\\n## Detailed Results")
        for result in results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report.append(f"### {result.name} - {status}")
            report.append(f"- Duration: {result.duration:.3f}s")
            report.append(f"- Memory Usage: {result.memory_usage:.2f}MB")
            report.append(f"- Operations/Second: {result.operations_per_second:.1f}")
            if result.error_message:
                report.append(f"- Error: {result.error_message}")
            if result.metadata:
                report.append("- Metadata:")
                for key, value in result.metadata.items():
                    report.append(f"  - {key}: {value}")

        # Comparison with baseline
        if comparison:
            report.append("\\n## Baseline Comparison")

            if comparison["regressions"]:
                report.append("### ⚠️ Performance Regressions Detected")
                for regression in comparison["regressions"]:
                    report.append(f"- {regression['name']}:")
                    report.append(
                        f"  - Duration: {regression['duration_change']:+.1f}%"
                    )
                    report.append(f"  - Memory: {regression['memory_change']:+.1f}%")
                    report.append(
                        f"  - Operations/sec: {regression['ops_change']:+.1f}%"
                    )

            if comparison["improvements"]:
                report.append("### 🎉 Performance Improvements Detected")
                for improvement in comparison["improvements"]:
                    report.append(f"- {improvement['name']}:")
                    report.append(
                        f"  - Duration: {improvement['duration_change']:+.1f}%"
                    )
                    report.append(f"  - Memory: {improvement['memory_change']:+.1f}%")
                    report.append(
                        f"  - Operations/sec: {improvement['ops_change']:+.1f}%"
                    )

            if not comparison["regressions"] and not comparison["improvements"]:
                report.append("### ✅ No significant changes from baseline")

        # Alerts
        if self.config["reporting"]["alert_on_regression"]:
            failed_tests = [r for r in results if not r.success]
            if failed_tests:
                report.append("\\n## 🚨 ALERTS")
                report.append("### Failed Tests")
                for test in failed_tests:
                    report.append(
                        f"- {test.name}: {test.error_message or 'Performance threshold exceeded'}"
                    )

        return "\\n".join(report)

    def save_report(self, results: List[BenchmarkResult], comparison: Dict[str, Any]):
        """Save benchmark report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(f"performance_report_{timestamp}.md")

        report_content = self.generate_report(results, comparison)

        with open(report_path, "w") as f:
            f.write(report_content)

        print(f"📄 Report saved to {report_path}")
        return report_path


def main():
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(description="Performance Benchmarking Suite")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--baseline-only", action="store_true", help="Only save baseline, don't compare"
    )
    parser.add_argument("--output", help="Output directory for reports")

    args = parser.parse_args()

    # Change output directory if specified
    if args.output:
        os.chdir(args.output)

    # Run benchmarks
    benchmark = PerformanceBenchmark(args.config)
    results = benchmark.run_all_benchmarks()

    # Compare with baseline
    if not args.baseline_only:
        comparison = benchmark.compare_with_baseline(results)
    else:
        comparison = {}

    # Save baseline
    benchmark.save_baseline(results)

    # Generate and save report
    report_path = benchmark.save_report(results, comparison)

    # Print summary
    print("\\n" + "=" * 50)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 50)

    passed = sum(1 for r in results if r.success)
    total = len(results)

    print(f"Tests Passed: {passed}/{total} ({passed / total * 100:.1f}%)")

    if comparison.get("regressions"):
        print(f"\\n⚠️ Regressions: {len(comparison['regressions'])}")
        for reg in comparison["regressions"]:
            print(f"  - {reg['name']}: {reg['duration_change']:+.1f}% duration")

    if comparison.get("improvements"):
        print(f"\\n🎉 Improvements: {len(comparison['improvements'])}")
        for imp in comparison["improvements"]:
            print(f"  - {imp['name']}: {imp['ops_change']:+.1f}% operations/sec")

    print(f"\\n📄 Full report: {report_path}")

    # Exit with error code if benchmarks failed
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
