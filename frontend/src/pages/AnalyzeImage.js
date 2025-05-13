import React, { useState, useContext, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Alert, 
  Divider 
} from '@mui/material';
import axios from 'axios';

import { AuthContext } from '../context/AuthContext';
import ImageUploader from '../components/ImageUploader';
import AnalysisResults from '../components/AnalysisResults';

const AnalyzeImage = () => {
  const { token } = useContext(AuthContext);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleImageSelect = (file) => {
    setSelectedFile(file);
    setAnalysisResults(null);
    setError(null);
  };
  
  const handleAnalyzeImage = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    // Create form data for file upload
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await axios.post('/api/predictions/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      
      setAnalysisResults(response.data);
    } catch (err) {
      console.error('Error analyzing image:', err);
      setError(err.response?.data?.detail || 'Error analyzing image. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Automatically analyze when file is selected
  useEffect(() => {
    if (selectedFile) {
      handleAnalyzeImage();
    }
  }, [selectedFile]); // eslint-disable-line react-hooks/exhaustive-deps
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Analyze Medical Image
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload an X-ray image for AI-powered analysis
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Upload Image
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ImageUploader 
          onImageSelect={handleImageSelect} 
          loading={loading} 
        />
      </Paper>
      
      {analysisResults && !loading && (
        <AnalysisResults results={analysisResults} />
      )}
      
      {!analysisResults && !loading && (
        <Paper sx={{ p: 3, bgcolor: '#f5f8fa' }}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            About This Tool
          </Typography>
          <Typography variant="body2" paragraph>
            This tool uses deep learning to analyze chest X-ray images for conditions such as pneumonia. 
            The analysis provides three key outputs:
          </Typography>
          <ul>
            <li>
              <Typography variant="body2" paragraph>
                <strong>Classification:</strong> Determines if the image shows signs of abnormality, 
                with a confidence score indicating the model's certainty.
              </Typography>
            </li>
            <li>
              <Typography variant="body2" paragraph>
                <strong>Heatmap Visualization:</strong> Highlights regions that influenced the model's decision, 
                making the AI's analysis more interpretable.
              </Typography>
            </li>
            <li>
              <Typography variant="body2" paragraph>
                <strong>Segmentation:</strong> For abnormal cases, outlines the regions that may contain 
                pathological conditions.
              </Typography>
            </li>
          </ul>
          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
            Note: For best results, use frontal (PA or AP) chest X-ray images in JPEG or PNG format.
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default AnalyzeImage; 