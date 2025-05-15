import os
import requests
import zipfile
import io
import shutil

# Create directories
def create_directories():
    """Create necessary directories for data"""
    os.makedirs("backend/data/train/normal", exist_ok=True)
    os.makedirs("backend/data/train/pneumonia", exist_ok=True)
    os.makedirs("backend/data/val/normal", exist_ok=True)
    os.makedirs("backend/data/val/pneumonia", exist_ok=True)
    print("Created data directories")

# Download a small sample of chest X-ray data from GitHub
def download_sample_data():
    """Download a small sample of chest X-ray data for testing"""
    print("Downloading sample data (this may take a few minutes)...")
    
    # Sample data URL (this is a placeholder - replace with a real source for sample data)
    url = "https://github.com/ieee8023/covid-chestxray-dataset/archive/refs/heads/master.zip"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Extract the ZIP file
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall("temp_data")
        
        # Move a few sample images to our data directories
        # Note: These paths need to be adapted based on the actual downloaded dataset structure
        sample_paths = [
            ("temp_data/covid-chestxray-dataset-master/images/", "backend/data/train/pneumonia/", 5),
            ("temp_data/covid-chestxray-dataset-master/images/", "backend/data/val/pneumonia/", 2),
        ]
        
        for source_dir, dest_dir, count in sample_paths:
            files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:count]
            for file in files:
                shutil.copy(os.path.join(source_dir, file), os.path.join(dest_dir, file))
        
        # Create some placeholder normal images (in a real scenario, you'd use actual normal X-rays)
        # Here we're just creating blank images for testing purposes
        import numpy as np
        from PIL import Image
        
        for i in range(5):
            img = np.ones((224, 224, 3), dtype=np.uint8) * 240  # Light gray image
            Image.fromarray(img).save(f"backend/data/train/normal/normal_{i}.png")
        
        for i in range(2):
            img = np.ones((224, 224, 3), dtype=np.uint8) * 240  # Light gray image
            Image.fromarray(img).save(f"backend/data/val/normal/normal_{i}.png")
        
        print("Sample data downloaded and organized.")
    except Exception as e:
        print(f"Error downloading or processing sample data: {e}")
    finally:
        # Clean up
        if os.path.exists("temp_data"):
            shutil.rmtree("temp_data")

if __name__ == "__main__":
    create_directories()
    download_sample_data()
    print("Finished. You can now train the model with: python -m backend.train") 