"""
Data Acquisition Agent FastAPI Router
Handles image upload and processing endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import uuid
from pathlib import Path
import aiofiles
from datetime import datetime
import logging

from backend.agents.data_acquisition.agent import DataAcquisitionAgent, ProcessingResult
from backend.shared.config import settings
from backend.shared.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the agent
data_agent = DataAcquisitionAgent()


@router.post("/process-scout-image", response_model=ProcessingResult)
async def process_scout_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    gps_latitude: Optional[float] = Form(None),
    gps_longitude: Optional[float] = Form(None),
    scout_id: Optional[str] = Form(None),
    shop_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Process an image uploaded by a Kade Scout
    
    Args:
        image: Uploaded image file
        gps_latitude: GPS latitude coordinate
        gps_longitude: GPS longitude coordinate  
        scout_id: ID of the scout who submitted the image
        shop_name: Name of the shop (if known)
        
    Returns:
        ProcessingResult with extracted product data
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Check file size
        contents = await image.read()
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique filename
        file_extension = Path(image.filename).suffix
        if file_extension.lower() not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension {file_extension} not allowed"
            )
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = Path(settings.UPLOAD_DIR) / "scout_images" / unique_filename
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        logger.info(f"Saved scout image: {file_path}")
        
        # Process image with the agent
        gps_coords = None
        if gps_latitude is not None and gps_longitude is not None:
            gps_coords = (gps_latitude, gps_longitude)
        
        metadata = {
            "scout_id": scout_id,
            "shop_name": shop_name,
            "upload_timestamp": datetime.now().isoformat(),
            "original_filename": image.filename
        }
        
        result = await data_agent.process_image(
            image_path=str(file_path),
            gps_coords=gps_coords,
            metadata=metadata
        )
        
        # Add background task to save to database if processing was successful
        if result.success and result.product_data:
            background_tasks.add_task(
                save_processed_data,
                result.product_data,
                str(file_path),
                gps_coords,
                scout_id,
                db
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing scout image: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing image"
        )


@router.post("/batch-process")
async def batch_process_images(
    images: List[UploadFile] = File(...),
    scout_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Process multiple images in batch for bulk data collection
    """
    if len(images) > 10:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images per batch"
        )
    
    results = []
    
    for image in images:
        try:
            # Process each image (simplified version)
            contents = await image.read()
            
            # Generate unique filename
            file_extension = Path(image.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = Path(settings.UPLOAD_DIR) / "scout_images" / "batch" / unique_filename
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)
            
            # Process image
            result = await data_agent.process_image(str(file_path))
            results.append({
                "filename": image.filename,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Error processing {image.filename}: {e}")
            results.append({
                "filename": image.filename,
                "error": str(e)
            })
    
    return {"batch_results": results}


@router.get("/processing-stats")
async def get_processing_stats(db: Session = Depends(get_db)):
    """
    Get statistics about image processing
    """
    # This would query the database for processing statistics
    # For now, return mock data
    return {
        "total_images_processed": 1250,
        "successful_extractions": 1100,
        "average_confidence_score": 0.85,
        "most_common_brands": [
            {"brand": "Anchor", "count": 245},
            {"brand": "Maliban", "count": 189},
            {"brand": "Munchee", "count": 167}
        ],
        "processing_time_stats": {
            "average_ms": 2500,
            "median_ms": 2200,
            "95th_percentile_ms": 4800
        }
    }


@router.post("/validate-extraction")
async def validate_extraction(
    image_id: str,
    is_correct: bool,
    corrected_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """
    Allow scouts or admin to validate/correct AI extractions
    This helps improve the model over time
    """
    try:
        # Here we would:
        # 1. Find the original extraction in database
        # 2. Store the validation feedback
        # 3. Update confidence scores
        # 4. Potentially retrain models
        
        validation_data = {
            "image_id": image_id,
            "is_correct": is_correct,
            "corrected_data": corrected_data,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Save validation to database
        # This would be implemented with actual database models
        
        return {
            "message": "Validation recorded successfully",
            "validation_id": str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"Error recording validation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error recording validation"
        )


async def save_processed_data(
    product_data,
    image_path: str,
    gps_coords: Optional[tuple],
    scout_id: Optional[str],
    db: Session
):
    """
    Background task to save processed data to database
    """
    try:
        # This would save the extracted product data to the database
        # Along with the image path, GPS coordinates, and scout information
        logger.info(f"Saving processed data for product: {product_data.product_name}")
        
        # Implementation would involve:
        # 1. Creating database record for the extraction
        # 2. Linking to scout and location
        # 3. Updating inventory if product exists
        # 4. Creating new product if doesn't exist
        
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")


@router.get("/health")
async def health_check():
    """Health check for the data acquisition service"""
    return {
        "status": "healthy",
        "service": "data-acquisition-agent",
        "timestamp": datetime.now().isoformat()
    }
