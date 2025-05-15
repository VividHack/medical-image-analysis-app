import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from backend.models.classification_model import MedicalImageClassifier
from backend.models.segmentation_model import UNet

# Training configuration
CONFIG = {
    "classifier": {
        "batch_size": 32,
        "learning_rate": 0.001,
        "epochs": 20,
        "num_classes": 2,
        "model_save_path": os.path.join("backend", "models", "weights", "classifier.pth")
    },
    "segmenter": {
        "batch_size": 16,
        "learning_rate": 0.001,
        "epochs": 30,
        "model_save_path": os.path.join("backend", "models", "weights", "segmenter.pth")
    },
    "data": {
        "train_dir": os.path.join("backend", "data", "train"),
        "val_dir": os.path.join("backend", "data", "val"),
        "segmentation_train_dir": os.path.join("backend", "data", "segmentation", "train"),
        "segmentation_val_dir": os.path.join("backend", "data", "segmentation", "val")
    }
}

def train_classifier(device):
    """
    Train the classification model
    """
    print("Training classification model...")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(CONFIG["classifier"]["model_save_path"]), exist_ok=True)
    
    # Data transformations
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load datasets
    train_dataset = datasets.ImageFolder(
        CONFIG["data"]["train_dir"], 
        transform=train_transform
    )
    
    val_dataset = datasets.ImageFolder(
        CONFIG["data"]["val_dir"], 
        transform=val_transform
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=CONFIG["classifier"]["batch_size"], 
        shuffle=True
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=CONFIG["classifier"]["batch_size"]
    )
    
    # Initialize model
    model = MedicalImageClassifier(num_classes=CONFIG["classifier"]["num_classes"])
    model = model.to(device)
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG["classifier"]["learning_rate"])
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 'min', patience=3, factor=0.1, verbose=True
    )
    
    # Training loop
    best_val_loss = float('inf')
    
    for epoch in range(CONFIG["classifier"]["epochs"]):
        # Training phase
        model.train()
        train_loss = 0.0
        train_preds = []
        train_targets = []
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Zero the gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Track statistics
            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_preds.extend(predicted.cpu().numpy())
            train_targets.extend(labels.cpu().numpy())
        
        # Calculate training metrics
        train_loss /= len(train_loader)
        train_acc = accuracy_score(train_targets, train_preds)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_preds = []
        val_targets = []
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                # Forward pass
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                # Track statistics
                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                val_preds.extend(predicted.cpu().numpy())
                val_targets.extend(labels.cpu().numpy())
        
        # Calculate validation metrics
        val_loss /= len(val_loader)
        val_acc = accuracy_score(val_targets, val_preds)
        val_precision = precision_score(val_targets, val_preds, average='weighted')
        val_recall = recall_score(val_targets, val_preds, average='weighted')
        val_f1 = f1_score(val_targets, val_preds, average='weighted')
        
        # Update learning rate
        scheduler.step(val_loss)
        
        # Print statistics
        print(f"Epoch {epoch+1}/{CONFIG['classifier']['epochs']}")
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        print(f"Precision: {val_precision:.4f}, Recall: {val_recall:.4f}, F1: {val_f1:.4f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), CONFIG["classifier"]["model_save_path"])
            print(f"Model saved to {CONFIG['classifier']['model_save_path']}")
    
    print("Classification model training complete.")

def train_segmenter(device):
    """
    Train the segmentation model
    """
    print("Training segmentation model...")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(CONFIG["segmenter"]["model_save_path"]), exist_ok=True)
    
    # TODO: Implement custom dataset for segmentation
    # This requires paired data (images and masks)
    # For brevity, this implementation is left as a placeholder
    
    print("Segmentation model training not implemented in this version.")
    print("For a full implementation, you'll need paired data (images and masks).")

def main():
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Train models
    train_classifier(device)
    train_segmenter(device)

if __name__ == "__main__":
    main() 