import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  Chip,
  Divider,
  Link
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import VerifiedIcon from '@mui/icons-material/Verified';
import ErrorIcon from '@mui/icons-material/Error';

const ConfidenceIndicator = ({ confidence }) => {
  let color = '#4caf50';  // High confidence (green)
  let label = 'High';
  let icon = <VerifiedIcon />;
  
  if (confidence < 0.7) {
    color = '#ff9800';  // Medium confidence (amber)
    label = 'Medium';
  }
  
  if (confidence < 0.5) {
    color = '#f44336';  // Low confidence (red)
    label = 'Low';
    icon = <ErrorIcon />;
  }
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
      <Typography variant="body2" sx={{ mr: 1 }}>Confidence:</Typography>
      <Chip 
        icon={icon}
        label={`${label} (${Math.round(confidence * 100)}%)`}
        size="small"
        sx={{ 
          backgroundColor: `${color}20`, 
          color: color,
          fontWeight: 'bold'
        }} 
      />
    </Box>
  );
};

const AnalysisResults = ({ results }) => {
  if (!results) return null;
  
  const { prediction, confidence, segmentation_url, heatmap_url } = results;
  
  // Determine if the prediction is positive (disease detected)
  const isPositive = prediction !== 'Normal';
  
  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <AssessmentIcon sx={{ mr: 1 }} />
        Analysis Results
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card className="analysis-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>Diagnosis</Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Prediction:</Typography>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontWeight: 'bold',
                    color: isPositive ? '#f44336' : '#4caf50'
                  }}
                >
                  {prediction}
                </Typography>
              </Box>
              
              <ConfidenceIndicator confidence={confidence} />
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {isPositive ? (
                    'The analysis indicates the presence of abnormalities that may suggest a pathological condition. Please consult a healthcare professional for proper diagnosis.'
                  ) : (
                    'The analysis suggests no significant abnormalities. Regular check-ups are still recommended.'
                  )}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card className="analysis-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>Heatmap Visualization</Typography>
              <Divider sx={{ mb: 2 }} />
              
              {heatmap_url ? (
                <>
                  <img 
                    src={heatmap_url} 
                    alt="Heatmap visualization" 
                    className="result-image"
                  />
                  <Typography variant="body2" color="text.secondary">
                    The heatmap highlights regions that influenced the model's prediction, with warmer colors (red/yellow) indicating areas of higher importance.
                  </Typography>
                </>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Heatmap visualization not available.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card className="analysis-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>Segmentation</Typography>
              <Divider sx={{ mb: 2 }} />
              
              {segmentation_url && isPositive ? (
                <>
                  <img 
                    src={segmentation_url} 
                    alt="Segmentation mask" 
                    className="result-image"
                  />
                  <Typography variant="body2" color="text.secondary">
                    The segmentation mask outlines regions of potential abnormalities detected in the image.
                  </Typography>
                </>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    {isPositive 
                      ? 'Segmentation not available for this image.'
                      : 'Segmentation is only generated when abnormalities are detected.'}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Paper sx={{ p: 2, mt: 4, backgroundColor: '#f8f9fa' }}>
        <Typography variant="body2" color="text.secondary">
          <strong>Disclaimer:</strong> This analysis is for educational purposes only and should not be used for clinical diagnosis. 
          Always consult with a healthcare professional for proper medical advice and diagnosis.
        </Typography>
      </Paper>
    </Box>
  );
};

export default AnalysisResults; 