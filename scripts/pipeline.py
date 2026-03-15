#!/usr/bin/env python3
"""
pipeline.py

Runs the full gazetteer update pipeline in the correct order.
Use this after importing new data from the topical pipeline.

Steps:
  1. Validate coherence (detect issues)
  2. Calculate metrics (boost, priority → ACTIVE)
  3. Structure (generate clean flat files)
  4. Report (summary of changes)

Usage:
    # Full pipeline (requires topics V3 path)
    python scripts/pipeline.py --topics-dir ../bible-topics-dataset/data/01_unified

    # Validate only (no changes)
    python scripts/pipeline.py --validate-only

    # Skip validation (just metrics + structure)
    python scripts/pipeline.py --topics-dir ../bible-topics-dataset/data/01_unified --skip-validate
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
PYTHON = sys.executable


def run_step(name: str, cmd: list, allow_fail: bool = False) -> bool:
    print(f"\n{'='*60}")
    print(f"STEP: {name}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))

    if result.returncode != 0:
        if allow_fail:
            print(f"  WARNING: {name} reported issues (non-blocking)")
            return False
        else:
            print(f"  ERROR: {name} failed")
            sys.exit(1)

    print(f"  OK: {name} completed")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run full gazetteer update pipeline")
    parser.add_argument("--topics-dir", type=Path, help="Path to topics V3 for metrics calculation")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation, no changes")
    parser.add_argument("--skip-validate", action="store_true", help="Skip validation step")
    args = parser.parse_args()

    print("=" * 60)
    print("GAZETTEER UPDATE PIPELINE")
    print("=" * 60)

    # Step 1: Validate
    if not args.skip_validate:
        run_step(
            "Validate coherence",
            [PYTHON, str(SCRIPTS_DIR / "validate_coherence.py")],
            allow_fail=True,  # Issues are reported but don't block
        )

    if args.validate_only:
        print("\n(validate-only mode — stopping here)")
        return

    # Step 2: Calculate metrics
    if not args.topics_dir:
        print("\nERROR: --topics-dir required for metrics calculation")
        sys.exit(1)

    if not args.topics_dir.exists():
        print(f"\nERROR: Topics dir not found: {args.topics_dir}")
        sys.exit(1)

    run_step(
        "Calculate metrics",
        [PYTHON, str(SCRIPTS_DIR / "calculate_metrics.py"), "--topics-dir", str(args.topics_dir)],
    )

    # Step 3: Structure
    run_step(
        "Generate structured files",
        [PYTHON, str(SCRIPTS_DIR / "structure.py")],
    )

    # Summary
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("Next steps:")
    print("  1. Review changes: git diff --stat")
    print("  2. Commit: git add -A && git commit -m 'feat: update gazetteers'")
    print("  3. Push: git push")


if __name__ == "__main__":
    main()
