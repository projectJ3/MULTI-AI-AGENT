import subprocess
import threading
import time
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

def run_backend():
    try:
        logger.info("Starting backend service..")
        subprocess.run(
            ["uvicorn", "app.backend.api:app", "--host", "127.0.0.1", "--port", "9999"],
            check=True
        )
    except Exception as e:     # FIX: catch real errors
        logger.exception("Backend crashed")
        raise CustomException("Failed to start backend", error_detail=e)

def run_frontend():
    try:
        logger.info("Starting frontend service..")
        subprocess.run(["streamlit", "run", "app/frontend/ui.py"], check=True)
    except Exception as e:    # FIX: catch real errors
        logger.exception("Frontend crashed")
        raise CustomException("Failed to start frontend", error_detail=e)

if __name__ == "__main__":
    try:
        t = threading.Thread(target=run_backend, daemon=True)
        t.start()
        time.sleep(2)
        run_frontend()
    except Exception as e:
        logger.exception(f"Exception occurred: {e}")
