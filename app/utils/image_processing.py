import os
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
import uuid
import cv2
import matplotlib.pyplot as plt

# Image transformation for model input
def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

# Save uploaded image to disk
def save_uploaded_image(file, upload_dir="app/public/images/uploads"):
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.png"
    file_path = os.path.join(upload_dir, filename)
    
    # Read image data
    contents = file.file.read()
    
    # Save to disk
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return file_path

# Prepare image for model inference
def prepare_image(image_path):
    img = Image.open(image_path).convert('RGB')
    transform = get_transform()
    img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
    return img_tensor

# Generate Grad-CAM heatmap
def generate_gradcam(model, img_tensor, target_layer):
    # Save original gradients
    gradients = []
    
    # Hook for gradients
    def save_gradient(grad):
        gradients.append(grad)
    
    # Get the target layer's output
    for name, module in model.named_modules():
        if name == target_layer:
            module.register_backward_hook(save_gradient)
    
    # Forward pass
    output = model(img_tensor)
    pred_class = output.argmax().item()
    
    # Zero gradients
    model.zero_grad()
    
    # Backward pass with the predicted class
    output[0, pred_class].backward()
    
    # Get gradients and activations
    gradients = gradients[0].cpu().data.numpy()[0]
    activations = getattr(model, target_layer.split('.')[0])[int(target_layer.split('.')[1])].activations.cpu().data.numpy()[0]
    
    # Global average pooling
    weights = np.mean(gradients, axis=(1, 2))
    
    # Generate heatmap
    heatmap = np.zeros((activations.shape[1], activations.shape[2]), dtype=np.float32)
    for i, w in enumerate(weights):
        heatmap += w * activations[i, :, :]
    
    heatmap = np.maximum(heatmap, 0)
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-10)
    heatmap = np.uint8(255 * heatmap)
    
    return heatmap

# Save heatmap overlay
def save_heatmap(image_path, heatmap, save_dir="app/public/images/heatmaps"):
    os.makedirs(save_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}_heatmap.png"
    save_path = os.path.join(save_dir, filename)
    
    # Load original image
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    
    # Resize heatmap
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    
    # Apply colormap to heatmap
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    
    # Overlay heatmap on original image
    superimposed = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
    
    # Save overlay
    cv2.imwrite(save_path, superimposed)
    
    return save_path

# Save segmentation mask
def save_segmentation(mask_array, save_dir="app/public/images/segmentations"):
    os.makedirs(save_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}_segmentation.png"
    save_path = os.path.join(save_dir, filename)
    
    # Convert to uint8
    mask = (mask_array * 255).astype(np.uint8)
    
    # Save mask
    cv2.imwrite(save_path, mask)
    
    return save_path 