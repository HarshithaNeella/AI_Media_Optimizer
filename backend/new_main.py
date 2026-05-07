from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict
from requests.exceptions import Timeout
import requests
import os

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI Media Optimization Backend",
    version="1.0.0"
)

# =========================================================
# ENABLE CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def home():

    return {
        "success": True,
        "message": "AI Media Optimization Backend Running"
    }

# =========================================================
# ANALYZE ENDPOINT
# =========================================================

@app.post("/analyze")
async def analyze(data: dict):

    try:

        # =================================================
        # N8N WEBHOOK URL
        # =================================================

        webhook_url = os.getenv(
            "N8N_WEBHOOK_URL",
            "http://localhost:5678/webhook/run-analysis"
        )

        # =================================================
        # SEND DATA TO N8N
        # =================================================

        response = requests.post(
            webhook_url,
            json=data,
            timeout=120
        )

        # =================================================
        # HANDLE HTTP FAILURE
        # =================================================

        if response.status_code != 200:

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"n8n workflow failed with status {response.status_code}",
                    "details": response.text
                }
            )

        # =================================================
        # PARSE JSON RESPONSE
        # =================================================

        try:

            workflow_result = response.json()

        except Exception:

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Invalid JSON returned from n8n"
                }
            )

        # =================================================
        # VALIDATE RESPONSE TYPE
        # =================================================

        if not isinstance(workflow_result, dict):

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "n8n must return a JSON object"
                }
            )

        # =================================================
        # RETURN CLEAN RESPONSE
        # =================================================

        return JSONResponse(content=workflow_result)

    # =====================================================
    # TIMEOUT ERROR
    # =====================================================

    except Timeout:

        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "error": "n8n workflow timeout"
            }
        )

    # =====================================================
    # GENERIC ERROR
    # =====================================================

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )