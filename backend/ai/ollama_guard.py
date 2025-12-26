"""
OLLAMA GUARD - Process Management for Ollama

This module provides:
1. Detection of lingering Ollama model processes
2. Safe cleanup/kill functionality
3. keep_alive=0 enforcement helper

SAFETY: Only affects processes matching Ollama patterns.
"""

import os
import re
import subprocess
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OllamaProcess:
    """Represents a detected Ollama process."""
    pid: int
    command: str
    model_name: Optional[str] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    running_since: Optional[str] = None


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    processes_found: List[OllamaProcess]
    processes_killed: List[int]
    errors: List[str]
    timestamp: float = field(default_factory=time.time)
    success: bool = True


class OllamaGuard:
    """
    Manages Ollama process lifecycle to prevent zombie processes.
    """
    
    # Patterns to identify Ollama model processes
    OLLAMA_PATTERNS = [
        r"ollama.*run",
        r"ollama.*serve",
        r"ollama_llama_server",
        r"llama\.cpp",
    ]
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._last_cleanup: Optional[CleanupResult] = None
    
    def detect_processes(self) -> List[OllamaProcess]:
        """
        Detect running Ollama-related processes.
        
        Works on macOS and Linux.
        """
        processes: List[OllamaProcess] = []
        
        try:
            # Use ps command to find processes
            if os.name == "nt":
                # Windows - limited support
                logger.warning("OllamaGuard: Windows detection not fully supported")
                return processes
            
            # Unix-like systems (macOS, Linux)
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"OllamaGuard: ps command failed: {result.stderr}")
                return processes
            
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            
            for line in lines:
                for pattern in self.OLLAMA_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        parts = line.split(None, 10)
                        if len(parts) >= 11:
                            try:
                                pid = int(parts[1])
                                cpu = float(parts[2])
                                mem = float(parts[3])
                                command = parts[10]
                                
                                # Extract model name if present
                                model_match = re.search(r"(?:run|serve)\s+(\S+)", command)
                                model_name = model_match.group(1) if model_match else None
                                
                                processes.append(OllamaProcess(
                                    pid=pid,
                                    command=command[:100],  # Truncate
                                    model_name=model_name,
                                    memory_mb=mem,
                                    cpu_percent=cpu,
                                ))
                            except (ValueError, IndexError) as e:
                                logger.debug(f"OllamaGuard: Failed to parse line: {e}")
                        break  # Found match, no need to check other patterns
                        
        except subprocess.TimeoutExpired:
            logger.error("OllamaGuard: ps command timed out")
        except Exception as e:
            logger.error(f"OllamaGuard: Error detecting processes: {e}")
        
        return processes
    
    async def unload_model(self, model_name: str) -> bool:
        """
        Explicitly unload a model from Ollama server.
        Uses keep_alive=0 approach.
        """
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Send a generate request with keep_alive=0 to unload
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "",
                        "keep_alive": 0,  # Unload immediately
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"OllamaGuard: Unloaded model {model_name}")
                    return True
                else:
                    logger.warning(f"OllamaGuard: Failed to unload {model_name}: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"OllamaGuard: Error unloading model {model_name}: {e}")
            return False
    
    async def unload_all_models(self) -> List[str]:
        """
        Unload all currently loaded models.
        """
        import httpx
        
        unloaded: List[str] = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # First, get list of running models
                response = await client.get(f"{self.base_url}/api/ps")
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    
                    for model_info in models:
                        model_name = model_info.get("name", model_info.get("model"))
                        if model_name:
                            if await self.unload_model(model_name):
                                unloaded.append(model_name)
                else:
                    logger.warning(f"OllamaGuard: Could not get running models: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"OllamaGuard: Error unloading all models: {e}")
        
        return unloaded
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        Kill a specific process by PID.
        
        Args:
            pid: Process ID to kill
            force: Use SIGKILL instead of SIGTERM
        """
        try:
            import signal
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
            logger.info(f"OllamaGuard: Killed process {pid} (force={force})")
            return True
        except ProcessLookupError:
            logger.debug(f"OllamaGuard: Process {pid} already terminated")
            return True
        except PermissionError:
            logger.error(f"OllamaGuard: Permission denied to kill process {pid}")
            return False
        except Exception as e:
            logger.error(f"OllamaGuard: Error killing process {pid}: {e}")
            return False
    
    async def cleanup(self, kill_lingering: bool = True) -> CleanupResult:
        """
        Full cleanup operation:
        1. Detect Ollama processes
        2. Unload all models via API
        3. Optionally kill lingering processes
        
        Returns CleanupResult with details.
        """
        result = CleanupResult(
            processes_found=[],
            processes_killed=[],
            errors=[],
        )
        
        # Step 1: Detect processes
        result.processes_found = self.detect_processes()
        logger.info(f"OllamaGuard: Found {len(result.processes_found)} Ollama processes")
        
        # Step 2: Try graceful unload via API
        try:
            unloaded = await self.unload_all_models()
            if unloaded:
                logger.info(f"OllamaGuard: Gracefully unloaded models: {unloaded}")
        except Exception as e:
            result.errors.append(f"Model unload failed: {e}")
        
        # Step 3: Wait briefly for graceful shutdown
        if kill_lingering and result.processes_found:
            await self._async_sleep(2)
            
            # Re-detect after grace period
            remaining = self.detect_processes()
            
            # Kill remaining processes (excluding main ollama serve)
            for proc in remaining:
                if "serve" not in proc.command.lower():
                    if self.kill_process(proc.pid):
                        result.processes_killed.append(proc.pid)
                    else:
                        result.errors.append(f"Failed to kill PID {proc.pid}")
        
        result.success = len(result.errors) == 0
        self._last_cleanup = result
        
        return result
    
    async def _async_sleep(self, seconds: float):
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(seconds)
    
    def get_last_cleanup(self) -> Optional[CleanupResult]:
        """Get result of last cleanup operation."""
        return self._last_cleanup
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Ollama guard status."""
        processes = self.detect_processes()
        return {
            "base_url": self.base_url,
            "active_processes": len(processes),
            "processes": [
                {
                    "pid": p.pid,
                    "command": p.command,
                    "model": p.model_name,
                    "memory_mb": p.memory_mb,
                    "cpu_percent": p.cpu_percent,
                }
                for p in processes
            ],
            "last_cleanup": {
                "timestamp": self._last_cleanup.timestamp if self._last_cleanup else None,
                "success": self._last_cleanup.success if self._last_cleanup else None,
                "processes_killed": self._last_cleanup.processes_killed if self._last_cleanup else [],
            } if self._last_cleanup else None,
        }


# =============================================================================
# MODULE-LEVEL HELPER
# =============================================================================

_guard_instance: Optional[OllamaGuard] = None


def get_ollama_guard() -> OllamaGuard:
    """Get the global OllamaGuard instance."""
    global _guard_instance
    if _guard_instance is None:
        from backend.ai.ai_authority import get_ai_authority
        base_url = get_ai_authority().get_ollama_base_url()
        _guard_instance = OllamaGuard(base_url=base_url)
    return _guard_instance
