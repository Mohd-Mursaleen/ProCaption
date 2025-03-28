from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
import os
from dotenv import load_dotenv
import asyncio
import time
from uvicorn.config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="ProCaptions: AI-Powered Image Text Editor",
    description="API for adding text behind image subjects using advanced AI segmentation"
)

# Configure server timeout settings - INCREASED TIMEOUTS
Config.TIMEOUT_KEEP_ALIVE = 300  # 5 minutes in seconds (increased from 120)
Config.HTTP_TIMEOUT = 300        # 5 minutes in seconds (increased from 120)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "original").mkdir(exist_ok=True)
(UPLOAD_DIR / "processed").mkdir(exist_ok=True)
(UPLOAD_DIR / "temp").mkdir(exist_ok=True)
(UPLOAD_DIR / "public").mkdir(exist_ok=True)

# Mount static files directory for serving uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/uploads/public", StaticFiles(directory="uploads/public"), name="public_uploads")

# Initialize Redis cache if environment variable set
try:
    if os.getenv("USE_REDIS", "false").lower() == "true":
        import redis
        logger.info("Setting up Redis cache")
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=True
        )
        # Test connection
        redis_client.ping()
        logger.info("Redis cache connected successfully")
    else:
        redis_client = None
        logger.info("Redis caching disabled")
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {str(e)}")
    redis_client = None

# Import routers
from src.routes import image_routes

# Include routers
app.include_router(image_routes.router, prefix="/api/v1")

# Download models on startup
@app.on_event("startup")
async def startup_event():
    # Run model download in background to avoid blocking startup
    asyncio.create_task(download_models())

async def download_models():
    try:
        from src.setup.download_models import setup_models
        await asyncio.to_thread(setup_models)
        logger.info("Model setup completed")
    except Exception as e:
        logger.error(f"Error during model setup: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    # Get more detailed health information
    health_info = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - app.state.start_time if hasattr(app.state, "start_time") else None,
        "cache": {
            "redis": "connected" if redis_client else "disabled",
        },
        "models": {
            "sam": {
                "available": False,
                "device": "unknown"
            },
            "yolo": {
                "available": False,
                "version": "unknown"
            },
            "rembg": {
                "available": False
            }
        }
    }
    
    # Import segmentation service to check model status
    try:
        from src.routes.image_routes import segmentation_service
        
        # Check SAM availability
        if hasattr(segmentation_service, "sam_predictor") and segmentation_service.sam_predictor is not None:
            health_info["models"]["sam"]["available"] = True
            # Get device info if possible
            if hasattr(segmentation_service.sam_predictor.model, "device"):
                health_info["models"]["sam"]["device"] = str(segmentation_service.sam_predictor.model.device)
        
        # Check YOLOv8 availability
        if hasattr(segmentation_service, "yolo_model") and segmentation_service.yolo_model is not None:
            health_info["models"]["yolo"]["available"] = True
            # Get version info if possible
            health_info["models"]["yolo"]["version"] = getattr(segmentation_service.yolo_model, "version", "unknown")
        
        # Check rembg availability
        try:
            from rembg import remove
            health_info["models"]["rembg"]["available"] = True
        except ImportError:
            health_info["models"]["rembg"]["available"] = False
            
    except Exception as e:
        logger.error(f"Error checking model status: {str(e)}")
    
    return health_info

# Record app start time for uptime tracking
@app.on_event("startup")
async def record_start_time():
    app.state.start_time = time.time() 