# tools/test_wizard.py
"""
Truth Audit Test Wizard
=======================

Single authoritative entrypoint to execute the full test framework
in a safe, deterministic, governance-aware manner.

NO direct pytest usage is allowed outside this wizard.

Phases:
1. Truth Core (no AI, no MCP)
2. Governance Enforcement
3. Structural Pipeline (offline structural mode)
4. AI Integration (MCP required)

Authoritative by design.
"""

import argparse
import os
import subprocess
import sys
import time
from typing import List


# ---------------------------
# Configuration
# ---------------------------

PYTHON = sys.executable

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PHASES = [
    "truth_core",
    "governance",
    "structural",
    "ai",
]

PHASE_TESTS = {
    "truth_core": [
        "backend/tests/unit",
        "backend/tests/integration/test_registry_purity.py",
        "backend/tests/test_core_summary_backbone.py",
    ],
    "governance": [
        "backend/tests/unit/test_governance_config.py",
        "backend/tests/unit/test_governance_api.py",
        "backend/tests/integration/test_enforcement_laws.py",
    ],
    "structural": [
        "backend/tests",
    ],
    "ai": [
        "backend/tests",
    ],
}

PHASE_PYTEST_ARGS = {
    "truth_core": [],
    "governance": [],
    "structural": ["-k", "structural"],
    "ai": ["-k", "ai"],
}


# ---------------------------
# Utilities
# ---------------------------

def die(msg: str) -> None:
    print(f"\n⛔ FATAL: {msg}")
    sys.exit(1)


def banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def run(cmd: List[str], env: dict) -> None:
    print(f"\n▶ RUN: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
    )
    if result.returncode != 0:
        die("Test phase failed")


# ---------------------------
# Governance / Environment Checks
# ---------------------------

def validate_environment(mode: str) -> None:
    env = os.getenv("ENV", "DEV").upper()

    print(f"Environment detected: {env}")

    if env == "PRODUCTION":
        if mode != "full":
            die("PRODUCTION may only run FULL test mode")
        print("✔ Production environment locked")

    if env not in {"DEV", "TEST", "PRODUCTION"}:
        die(f"Invalid ENV value: {env}")


def validate_governance_preflight(mode: str) -> None:
    """
    Hard guarantees before running anything.
    """
    print("Running governance preflight checks...")

    if mode == "structural":
        # structural mode requires explicit opt-in
        if os.getenv("ALLOW_OFFLINE_STRUCTURAL_MODE") != "1":
            die(
                "offline_structural_mode requested but "
                "ALLOW_OFFLINE_STRUCTURAL_MODE != 1"
            )

    print("✔ Governance preflight OK")


# ---------------------------
# MCP Handling
# ---------------------------

def check_mcp_health() -> None:
    """
    Minimal MCP health check.
    Assumes MCP exposes http://localhost:3333/health
    """
    import urllib.request

    url = os.getenv("MCP_HEALTH_URL", "http://localhost:3333/health")

    print(f"Checking MCP health at {url} ...")

    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            if resp.status != 200:
                die("MCP health endpoint returned non-200")
    except Exception as e:
        die(f"MCP health check failed: {e}")

    print("✔ MCP is healthy")


# ---------------------------
# Phase Execution
# ---------------------------

def run_phase(phase: str, base_env: dict) -> None:
    banner(f"PHASE: {phase.upper()}")

    env = dict(base_env)

    # Phase-specific governance toggles
    if phase == "structural":
        env["ALLOW_OFFLINE_STRUCTURAL_MODE"] = "1"
        env["ENV"] = env.get("ENV", "DEV")

    if phase == "ai":
        check_mcp_health()

    cmd = [
        PYTHON,
        "-m",
        "pytest",
        *PHASE_TESTS[phase],
        *PHASE_PYTEST_ARGS.get(phase, []),
        "-v",
        "--tb=short",
    ]

    run(cmd, env)

    print(f"✔ Phase {phase} PASSED")


# ---------------------------
# Main Wizard
# ---------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Truth Audit Test Wizard")
    parser.add_argument(
        "--mode",
        choices=["full", "structural"],
        default="full",
        help="Test execution mode",
    )
    args = parser.parse_args()

    mode = args.mode

    banner("Truth Audit Test Wizard")

    validate_environment(mode)
    validate_governance_preflight(mode)

    base_env = os.environ.copy()
    base_env.setdefault("ENV", "DEV")

    phases_to_run = PHASES if mode == "full" else ["truth_core", "governance", "structural"]

    for phase in phases_to_run:
        run_phase(phase, base_env)

    banner("ALL TEST PHASES PASSED")
    print("SYSTEM STATUS: TRUSTED")
    print("Truth, Governance, and Architecture are in sync.")


if __name__ == "__main__":
    main()
