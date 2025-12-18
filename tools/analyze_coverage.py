#!/usr/bin/env python3
"""
Analyze coverage.json to identify priority testing targets.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_coverage() -> None:
    """Analyze coverage data and output priority testing targets."""
    coverage_file = Path("coverage.json")

    if not coverage_file.exists():
        print("Error: coverage.json not found. Run pytest with --cov-report=json first.")
        return

    with open(coverage_file) as f:
        data = json.load(f)

    # Extract file coverage
    files_data: List[Tuple[str, float, int, int]] = []

    for file_path, file_data in data["files"].items():
        summary = file_data["summary"]
        total_stmts = summary["num_statements"]
        covered = summary["covered_lines"]

        if total_stmts > 0:
            coverage_pct = (covered / total_stmts) * 100
            files_data.append((file_path, coverage_pct, total_stmts, covered))

    # Sort by coverage percentage (ascending)
    files_data.sort(key=lambda x: x[1])

    # Categorize files
    critical_low = []  # <70%
    moderate = []      # 70-89%
    good = []          # >=90%

    for file_path, coverage, total, covered in files_data:
        # Skip __init__.py files and gui.py (intentionally skipped)
        if "__init__.py" in file_path or "gui.py" in file_path:
            continue

        if coverage < 70:
            critical_low.append((file_path, coverage, total, covered))
        elif coverage < 90:
            moderate.append((file_path, coverage, total, covered))
        else:
            good.append((file_path, coverage, total, covered))

    # Print analysis
    print("=" * 80)
    print("COVERAGE ANALYSIS - PRIORITY TESTING TARGETS")
    print("=" * 80)
    print()

    print(f"Total Files Analyzed: {len(files_data)}")
    print(f"Critical Low (<70%): {len(critical_low)}")
    print(f"Moderate (70-89%): {len(moderate)}")
    print(f"Good (>=90%): {len(good)}")
    print()

    print("=" * 80)
    print("CRITICAL LOW COVERAGE (<70%) - IMMEDIATE PRIORITY")
    print("=" * 80)
    for file_path, coverage, total, covered in critical_low:
        missing = total - covered
        print(f"{file_path:60s} {coverage:5.1f}% ({missing:4d} lines missing)")
    print()

    print("=" * 80)
    print("MODERATE COVERAGE (70-89%) - HIGH PRIORITY")
    print("=" * 80)
    for file_path, coverage, total, covered in moderate:
        missing = total - covered
        print(f"{file_path:60s} {coverage:5.1f}% ({missing:4d} lines missing)")
    print()

    print("=" * 80)
    print("GOOD COVERAGE (>=90%) - MAINTAIN")
    print("=" * 80)
    print(f"Total modules with >=90% coverage: {len(good)}")
    print()

    # Calculate effort estimate
    total_missing_critical = sum(total - covered for _, _, total, covered in critical_low)
    total_missing_moderate = sum(total - covered for _, _, total, covered in moderate)

    # Rough estimate: 1 test per 10 lines of missing coverage
    tests_needed_critical = total_missing_critical // 10
    tests_needed_moderate = total_missing_moderate // 10

    print("=" * 80)
    print("EFFORT ESTIMATE")
    print("=" * 80)
    print(f"Critical modules: ~{total_missing_critical} lines uncovered → ~{tests_needed_critical} tests needed")
    print(f"Moderate modules: ~{total_missing_moderate} lines uncovered → ~{tests_needed_moderate} tests needed")
    print(f"Total estimated tests: ~{tests_needed_critical + tests_needed_moderate}")
    print()

if __name__ == "__main__":
    analyze_coverage()
