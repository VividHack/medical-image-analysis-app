import os
import torch
import numpy as np
import boto3
from botocore.exceptions import ClientError

from backend.models.classification_model import MedicalImageClassifier, load_model as load_classifier
from backend.models.segmentation_model import load_model as load_segmenter
from backend.utils.image_processing import (
    prepare_image, 
    generate_gradcam,
    save_heatmap,
    save_segmentation
)

# Load models on startup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define class labels (customize based on your dataset)
CLASS_LABELS = ["Normal", "Pneumonia"]

# S3 Configuration from environment variables
S3_MODEL_BUCKET = os.getenv("S3_MODEL_BUCKET")
S3_CLASSIFIER_KEY = os.getenv("S3_CLASSIFIER_KEY", "classifier.pth") # Default key in bucket
S3_SEGMENTER_KEY = os.getenv("S3_SEGMENTER_KEY", "segmenter.pth")   # Default key in bucket
LOCAL_MODEL_TEMP_DIR = "/tmp/models" # Temporary directory inside the container

# Ensure the local temp directory exists
os.makedirs(LOCAL_MODEL_TEMP_DIR, exist_ok=True)

def _download_model_from_s3(bucket_name, object_key, local_path):
    if not bucket_name:
        print(f"INFO: S3_MODEL_BUCKET not set. Skipping download for {object_key}.")
        return False
    
    print(f"Attempting to download s3://{bucket_name}/{object_key} to {local_path}...")
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, object_key, local_path)
        print(f"Successfully downloaded model to {local_path}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"ERROR: Model file s3://{bucket_name}/{object_key} not found.")
        elif e.response['Error']['Code'] == '403':
             print(f"ERROR: Access denied for S3 object s3://{bucket_name}/{object_key}. Check IAM permissions.")
        else:
            print(f"ERROR: Failed to download model s3://{bucket_name}/{object_key}: {e}")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred downloading {object_key}: {e}")
        return False

class MedicalImageAnalyzer:
    def __init__(self):
        self.device = device
        self.classifier = None
        self.segmenter = None

        # Define local paths for downloaded models
        # Use os.path.basename to ensure we are only getting the filename part from S3 keys
        local_classifier_path = os.path.join(LOCAL_MODEL_TEMP_DIR, os.path.basename(S3_CLASSIFIER_KEY))
        local_segmenter_path = os.path.join(LOCAL_MODEL_TEMP_DIR, os.path.basename(S3_SEGMENTER_KEY))
        
        # Attempt to load classifier from S3, then local, then default
        classifier_ready = False
        if S3_MODEL_BUCKET: # Only attempt S3 download if bucket is configured
            if _download_model_from_s3(S3_MODEL_BUCKET, S3_CLASSIFIER_KEY, local_classifier_path):
                if os.path.exists(local_classifier_path):
                    try:
                        self.classifier = load_classifier(local_classifier_path, self.device)
                        print(f"INFO: Custom classifier loaded successfully from S3 via {local_classifier_path}")
                        classifier_ready = True
                    except Exception as e:
                        print(f"ERROR: Failed to load classifier from S3-downloaded file {local_classifier_path}: {e}")
        
        if not classifier_ready:
            # Fallback to local file system path if S3 not configured or failed
            legacy_classifier_path = os.path.join("backend", "models", "weights", "classifier.pth")
            if os.path.exists(legacy_classifier_path):
                try:
                    self.classifier = load_classifier(legacy_classifier_path, self.device)
                    print(f"INFO: Custom classifier loaded successfully from local path {legacy_classifier_path}")
                    classifier_ready = True
                except Exception as e:
                    print(f"ERROR: Failed to load classifier from local file {legacy_classifier_path}: {e}")

        if not classifier_ready:
            print(f"WARNING: Classifier model weights not loaded from S3 or local path.")
            print("INFO: Initializing classifier with pre-trained ImageNet weights (ResNet50).")
            try:
                self.classifier = MedicalImageClassifier(num_classes=len(CLASS_LABELS), pretrained=True).to(self.device)
                self.classifier.eval() # Set to evaluation mode
                print("INFO: Default ResNet50 based classifier initialized successfully.")
            except Exception as e:
                print(f"ERROR: Failed to initialize default ResNet50 classifier: {e}")
                self.classifier = None # Ensure classifier is None if initialization fails

        # Attempt to load segmenter from S3, then local
        segmenter_ready = False
        if S3_MODEL_BUCKET: # Only attempt S3 download if bucket is configured
            if _download_model_from_s3(S3_MODEL_BUCKET, S3_SEGMENTER_KEY, local_segmenter_path):
                if os.path.exists(local_segmenter_path):
                    try:
                        self.segmenter = load_segmenter(local_segmenter_path, self.device)
                        print(f"INFO: Custom segmenter loaded successfully from S3 via {local_segmenter_path}")
                        segmenter_ready = True
                    except Exception as e:
                        print(f"ERROR: Failed to load segmenter from S3-downloaded file {local_segmenter_path}: {e}")

        if not segmenter_ready:
            # Fallback to local file system path if S3 not configured or failed
            legacy_segmenter_path = os.path.join("backend", "models", "weights", "segmenter.pth")
            if os.path.exists(legacy_segmenter_path):
                try:
                    self.segmenter = load_segmenter(legacy_segmenter_path, self.device)
                    print(f"INFO: Custom segmenter loaded successfully from local path {legacy_segmenter_path}")
                    segmenter_ready = True
                except Exception as e:
                    print(f"ERROR: Failed to load segmenter from local file {legacy_segmenter_path}: {e}")
        
        if not segmenter_ready:
            print(f"WARNING: Segmenter model weights not loaded from S3 or local path.")
            print("INFO: Proceeding without a segmenter. Segmentation will be skipped if applicable.")
            self.segmenter = None
    
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