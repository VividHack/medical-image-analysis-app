import os
import torch
import numpy as np

from app.models.classification_model import load_model as load_classifier
from app.models.segmentation_model import load_model as load_segmenter
from app.utils.image_processing import (
    prepare_image, 
    generate_gradcam,
    save_heatmap,
    save_segmentation
)

# Load models on startup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define class labels (customize based on your dataset)
CLASS_LABELS = ["Normal", "Pneumonia"]

class MedicalImageAnalyzer:
    def __init__(self):
        self.device = device
        
        # Define model paths
        self.classifier_path = os.path.join("app", "models", "weights", "classifier.pth")
        self.segmenter_path = os.path.join("app", "models", "weights", "segmenter.pth")
        
        # Load models if weights exist, otherwise prepare for training
        self.classifier = None
        self.segmenter = None
        
        if os.path.exists(self.classifier_path):
            self.classifier = load_classifier(self.classifier_path, self.device)
            print("INFO: Custom classifier loaded successfully.")
        else:
            print("WARNING: Classifier model weights not found at", self.classifier_path)
            print("INFO: Proceeding without a classifier. Analysis will be mocked.")

        if os.path.exists(self.segmenter_path):
            self.segmenter = load_segmenter(self.segmenter_path, self.device)
            print("INFO: Custom segmenter loaded successfully.")
        else:
            print("WARNING: Segmenter model weights not found at", self.segmenter_path)
            print("INFO: Proceeding without a segmenter.")
    
    def analyze_image(self, image_path):
        """
        Analyze a medical image for classification, segmentation, and heatmap
        """
        # Check if models are available
        if self.classifier is None:
            print("WARNING: Classifier model not loaded. Returning mocked analysis.")
            return {
                "prediction": "Not Available (Model Not Loaded)",
                "confidence": 0.0,
                "uncertainty": 0.0,
                "segmentation_path": None,
                "heatmap_path": None
            }
        
        # Prepare image tensor
        img_tensor = prepare_image(image_path)
        img_tensor = img_tensor.to(self.device)
        
        # Get classification results with uncertainty
        pred_class, confidence, uncertainty = self.classifier.predict_with_uncertainty(img_tensor)
        class_idx = pred_class.item()
        confidence_score = confidence.item()
        
        # Get class label
        prediction = CLASS_LABELS[class_idx]
        
        # Generate segmentation if model is available
        segmentation_path = None
        if self.segmenter is not None and class_idx > 0:  # Only segment if disease is detected
            mask = self.segmenter.predict(img_tensor)
            mask_np = mask.cpu().numpy()[0, 0]  # Get the mask as a numpy array
            segmentation_path = save_segmentation(mask_np)
        elif self.segmenter is None and class_idx > 0:
            print("INFO: Segmentation skipped as segmenter model is not loaded.")
        
        # Generate heatmap
        grad_cam_layer = self.classifier.get_gradcam_layer()
        heatmap = generate_gradcam(self.classifier, img_tensor, grad_cam_layer)
        heatmap_path = save_heatmap(image_path, heatmap)
        
        return {
            "prediction": prediction,
            "confidence": confidence_score,
            "uncertainty": uncertainty.item() if isinstance(uncertainty, torch.Tensor) else uncertainty,
            "segmentation_path": segmentation_path,
            "heatmap_path": heatmap_path
        }

# Create a singleton instance
analyzer = MedicalImageAnalyzer() 