import asyncio
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

def safe_execute_async(coro):
    """
    Hardened bridge to run async code from sync contexts.
    Mitigates 'RuntimeError: asyncio.run() cannot be called from a running event loop'.
    
    Logic:
    1. If no loop is running in the current thread: use asyncio.run().
    2. If a loop is running in the current thread: offload to a dedicated 
       background thread to avoid loop conflicts and deadlocks.
    """
    try:
        # Detect existing loop in current thread
        loop = asyncio.get_running_loop()
        
        if loop.is_running():
            # Risk 1: Loop is already active. 
            # We offload to a temporary thread to run a new loop there.
            # This is the safest way to block a sync function called from async 
            # without requiring nest_asyncio.
            with concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncBridge") as pool:
                return pool.submit(asyncio.run, coro).result()
    except RuntimeError:
        # No loop in this thread, safe to use standard asyncio.run
        pass
    
    return asyncio.run(coro)
