from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from backend.database import get_db
from backend.models.database_models import User, Prediction
from backend.models.schemas import (
    Prediction as PredictionSchema,
    PredictionResponse
)
from backend.utils.auth import get_current_active_user
from backend.utils.image_processing import save_uploaded_image
from backend.models.inference import analyzer

router = APIRouter()

@router.post("/analyze", response_model=PredictionResponse)
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze a medical image and save the prediction
    """
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, JPEG, and PNG files are supported"
        )
    
    # Save uploaded image
    try:
        image_path = save_uploaded_image(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving image: {str(e)}"
        )
    
    # Analyze image
    try:
        result = analyzer.analyze_image(image_path)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}"
        )
    
    # Save prediction to database
    try:
        db_prediction = Prediction(
            user_id=current_user.id,
            image_path=image_path,
            prediction_result=result["prediction"],
            confidence_score=result["confidence"],
            segmentation_path=result.get("segmentation_path"),
            heatmap_path=result.get("heatmap_path")
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving prediction: {str(e)}"
        )
    
    # Convert paths to URLs
    segmentation_url = None
    if result.get("segmentation_path"):
        segmentation_url = f"/static/images/segmentations/{os.path.basename(result['segmentation_path'])}"
    
    heatmap_url = None
    if result.get("heatmap_path"):
        heatmap_url = f"/static/images/heatmaps/{os.path.basename(result['heatmap_path'])}"
    
    return {
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "segmentation_url": segmentation_url,
        "heatmap_url": heatmap_url
    }

@router.get("/history", response_model=List[PredictionSchema])
async def get_prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get prediction history for the current user
    """
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()
    return predictions

@router.get("/{prediction_id}", response_model=PredictionSchema)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific prediction
    """
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    return prediction 