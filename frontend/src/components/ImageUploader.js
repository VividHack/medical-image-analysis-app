import React, { useState, useRef } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress 
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImageIcon from '@mui/icons-material/Image';

const ImageUploader = ({ onImageSelect, loading }) => {
  const [previewImage, setPreviewImage] = useState(null);
  const fileInputRef = useRef(null);
  
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Check if file is an image
      if (!file.type.match('image.*')) {
        alert('Please select an image file (JPEG, PNG)');
        return;
      }
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size exceeds 10MB. Please select a smaller file.');
        return;
      }
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImage(e.target.result);
      };
      reader.readAsDataURL(file);
      
      // Pass file to parent component
      onImageSelect(file);
    }
  };
  
  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      const file = event.dataTransfer.files[0];
      
      // Check if file is an image
      if (!file.type.match('image.*')) {
        alert('Please select an image file (JPEG, PNG)');
        return;
      }
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImage(e.target.result);
      };
      reader.readAsDataURL(file);
      
      // Pass file to parent component
      onImageSelect(file);
    }
  };
  
  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };
  
  const handleClick = () => {
    fileInputRef.current.click();
  };
  
  return (
    <Box sx={{ mb: 4 }}>
      <input
        type="file"
        accept="image/jpeg, image/png"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        ref={fileInputRef}
      />
      
      <Box
        className="drop-zone"
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        sx={{
          pointerEvents: loading ? 'none' : 'auto',
          opacity: loading ? 0.7 : 1,
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="body1">Analyzing image...</Typography>
          </Box>
        ) : (
          <>
            {previewImage ? (
              <Box sx={{ textAlign: 'center' }}>
                <img 
                  src={previewImage} 
                  alt="Preview" 
                  className="image-preview" 
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Click or drag to change image
                </Typography>
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center' }}>
                <CloudUploadIcon sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Drag and drop an X-ray image
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or click to select from your computer
                </Typography>
                <Button 
                  variant="contained" 
                  startIcon={<ImageIcon />}
                  sx={{ mt: 2 }}
                  onClick={handleClick}
                >
                  Select Image
                </Button>
              </Box>
            )}
          </>
        )}
      </Box>
      
      {previewImage && !loading && (
        <Paper 
          elevation={0} 
          sx={{ 
            p: 2, 
            mt: 2, 
            backgroundColor: 'rgba(25, 118, 210, 0.05)',
            borderRadius: 2
          }}
        >
          <Typography variant="body2" color="text.secondary">
            <strong>Note:</strong> Upload a chest X-ray image for best results. The model is trained primarily on frontal chest X-rays for conditions like pneumonia.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default ImageUploader; 