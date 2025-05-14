import os
import torch
import numpy as np

from app.models.classification_model import MedicalImageClassifier, load_model as load_classifier
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
            # load_classifier internally uses MedicalImageClassifier(pretrained=False)
            # and then loads the state_dict from classifier_path
            self.classifier = load_classifier(self.classifier_path, self.device)
            print(f"INFO: Custom classifier loaded successfully from {self.classifier_path}")
        else:
            print(f"WARNING: Classifier model weights not found at {self.classifier_path}")
            print("INFO: Initializing classifier with pre-trained ImageNet weights (ResNet50).")
            try:
                # MedicalImageClassifier uses pretrained=True by default for ResNet50 backbone
                self.classifier = MedicalImageClassifier(num_classes=len(CLASS_LABELS), pretrained=True).to(self.device)
                self.classifier.eval() # Set to evaluation mode
                print("INFO: Default ResNet50 based classifier initialized successfully.")
            except Exception as e:
                print(f"ERROR: Failed to initialize default classifier: {e}")
                self.classifier = None # Ensure classifier is None if initialization fails

        if os.path.exists(self.segmenter_path):
            self.segmenter = load_segmenter(self.segmenter_path, self.device)
            print(f"INFO: Custom segmenter loaded successfully from {self.segmenter_path}")
        else:
            print(f"WARNING: Segmenter model weights not found at {self.segmenter_path}")
            print("INFO: Proceeding without a segmenter. Segmentation will be skipped if applicable.")
    
    def analyze_image(self, image_path):
        """
        Analyze a medical image for classification, segmentation, and heatmap
        """
        # Check if classifier is available
        if self.classifier is None:
            # This state indicates a failure during __init__ to load or initialize a classifier.
            raise ValueError("Classifier model is not available. Check logs for initialization errors.")
        
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