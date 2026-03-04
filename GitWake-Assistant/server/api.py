"""
api.py – FastAPI Cross-Device Server
=======================================
REST API server that allows any device on the LAN (including an Android
phone) to send commands to the GitWake Assistant.

Endpoints:
    POST /command       – Execute a text command
    GET  /health        – Health check
    GET  /history       – Command history
    POST /command/raw   – Execute a pre-parsed command dict

Run:
    uvicorn server.api:app --host 0.0.0.0 --port 8000

From phone/other device:
    curl -X POST http://<laptop-ip>:8000/command \\
         -H "Content-Type: application/json" \\
         -d '{"text": "open chrome"}'
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="GitWake Assistant API",
    description="Cross-device AI assistant REST API",
    version="1.0.0",
)

# Allow CORS from any origin (needed for cross-device communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────

class CommandRequest(BaseModel):
    """Request body for the /command endpoint."""
    text: str

    class Config:
        json_schema_extra = {
            "example": {"text": "open chrome"}
        }


class RawCommandRequest(BaseModel):
    """Request body for pre-parsed commands."""
    task: str
    params: dict[str, Any] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "task": "open_app",
                "params": {"app_name": "chrome"}
            }
        }


class CommandResponse(BaseModel):
    """Response body for command endpoints."""
    success: bool
    result: str
    parsed: dict[str, Any] = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "GitWake Assistant"}


@app.post("/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """
    Parse and execute a natural language command.

    Example:
        POST /command
        {"text": "open whatsapp and send nitin hello"}
    """
    try:
        from assistant_core.command_parser import CommandParser
        from assistant_core.executor import Executor

        parser = CommandParser()
        executor = Executor()

        # Parse the text into a structured command
        parsed = parser.parse(request.text)

        # Execute the command
        result = executor.execute(parsed)

        return CommandResponse(
            success="❌" not in result,
            result=result,
            parsed=parsed,
        )

    except Exception as e:
        logger.error(f"Command execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/command/raw", response_model=CommandResponse)
async def execute_raw_command(request: RawCommandRequest):
    """
    Execute a pre-parsed command dict.

    Example:
        POST /command/raw
        {"task": "open_app", "params": {"app_name": "chrome"}}
    """
    try:
        from assistant_core.executor import Executor

        executor = Executor()

        command = {"task": request.task, **request.params}
        result = executor.execute(command)

        return CommandResponse(
            success="❌" not in result,
            result=result,
            parsed=command,
        )

    except Exception as e:
        logger.error(f"Raw command error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = 20):
    """
    Get command history.

    Query params:
        limit: Max entries to return (default 20).
    """
    try:
        from assistant_core.memory import MemorySystem

        memory = MemorySystem()
        history = memory.get_history(limit=limit)
        return {"count": len(history), "history": history}

    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Server startup helper ────────────────────────────────────────────────────

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server (blocking)."""
    import uvicorn

    logger.info(f"Starting GitWake API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


def start_server_background(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server in a background thread."""
    import threading

    thread = threading.Thread(
        target=start_server,
        args=(host, port),
        daemon=True,
        name="GitWake-API-Server",
    )
    thread.start()
    logger.info(f"API server started in background on {host}:{port}")
    return thread
