import logging
import json
import time
from typing import Any, Dict, Optional
from functools import wraps

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("RTI-Trace")

class Tracer:
    """
    Simple tracing utility to log agent activities and tool calls.
    Mimics the observability patterns from Day 4 of the Kaggle Agents course.
    """
    
    @staticmethod
    def trace_agent(agent_name: str, action: str, inputs: Dict[str, Any] = None, outputs: Any = None, duration: float = 0.0):
        """
        Log a structured trace event.
        """
        event = {
            "type": "agent_trace",
            "agent": agent_name,
            "action": action,
            "inputs": inputs,
            "outputs": str(outputs)[:500] + "..." if outputs and len(str(outputs)) > 500 else outputs, # Truncate long outputs
            "duration_ms": round(duration * 1000, 2)
        }
        logger.info(json.dumps(event))

def trace_span(agent_name: str, action_name: str):
    """
    Decorator to trace a function execution as a span.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            inputs = {
                "args": [str(a) for a in args[1:]], # Skip self
                "kwargs": kwargs
            }
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                Tracer.trace_agent(agent_name, action_name, inputs, result, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                Tracer.trace_agent(agent_name, action_name, inputs, {"error": str(e)}, duration)
                raise
        return wrapper
    return decorator
