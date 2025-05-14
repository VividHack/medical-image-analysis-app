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
def generate_gradcam(model, img_tensor, target_layer_name):
    gradients = []
    activations_list = [] # Changed from 'activations' to avoid potential name clashes

    # Hook for gradients
    def backward_hook_fn(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    # Hook for activations
    def forward_hook_fn(module, input, output):
        activations_list.append(output)

    # Find the target layer module
    target_module = None
    for name, module_item in model.named_modules():
        if name == target_layer_name:
            target_module = module_item
            break
    
    if target_module is None:
        raise ValueError(f"Target layer '{target_layer_name}' not found in model.")

    # Register hooks
    # Use try-finally to ensure hooks are removed
    forward_handle = target_module.register_forward_hook(forward_hook_fn)
    backward_handle = target_module.register_backward_hook(backward_hook_fn) 

    heatmap_generated = None # Initialize to ensure it's defined for return
    try:
        # Forward pass to trigger hooks and get output
        output = model(img_tensor)
        
        if not activations_list:
             raise RuntimeError(f"Forward hook for activations on layer '{target_layer_name}' did not run or list is empty.")
        
        pred_class = output.argmax().item()
        
        model.zero_grad()
        # Backward pass with the predicted class to trigger gradient hook
        output[0, pred_class].backward()

        if not gradients:
            raise RuntimeError(f"Backward hook for gradients on layer '{target_layer_name}' did not run or list is empty.")

        # Get the hooked activations and gradients (using .detach() to be safe)
        act = activations_list[0].cpu().detach().numpy()[0]  # Assuming batch size 1, result shape: (C, H, W)
        grad = gradients[0].cpu().detach().numpy()[0]    # Assuming batch size 1, result shape: (C, H, W)

        # Global average pooling on gradients to get weights for channels
        weights = np.mean(grad, axis=(1, 2))  # Shape: (C,)
        
        # Weighted sum of activation maps (CAM)
        cam = np.zeros(act.shape[1:], dtype=np.float32) # Shape: (H, W)
        for i, w_val in enumerate(weights):
            cam += w_val * act[i, :, :]
        
        # Apply ReLU to the CAM
        cam = np.maximum(cam, 0)
        
        # Normalize CAM to 0-1 range for visualization
        if (np.max(cam) - np.min(cam)) > 1e-10 : # Avoid division by zero if cam is flat or all zeros
            cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam))
        else:
            cam = np.zeros_like(cam) # Or assign cam / (np.max(cam) + 1e-10)

        heatmap_generated = np.uint8(255 * cam)
        
    finally:
        # Always remove hooks
        forward_handle.remove()
        backward_handle.remove()
            
    if heatmap_generated is None:
        raise RuntimeError("Heatmap generation failed unexpectedly before returning.")

    return heatmap_generated

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