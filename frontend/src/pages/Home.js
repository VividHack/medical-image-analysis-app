import React, { useContext } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { 
  Container, 
  Box, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent,
  CardMedia,
  Divider
} from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import SpeedIcon from '@mui/icons-material/Speed';
import SchoolIcon from '@mui/icons-material/School';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

import { AuthContext } from '../context/AuthContext';

const features = [
  {
    icon: <AnalyticsIcon fontSize="large" color="primary" />,
    title: 'Advanced AI Analysis',
    description: 'Utilizes deep learning models to analyze medical images with high accuracy and provide detailed insights.'
  },
  {
    icon: <VerifiedUserIcon fontSize="large" color="primary" />,
    title: 'Explainable AI',
    description: 'Visualize regions of interest through heatmaps and segmentation, providing transparency in the analysis process.'
  },
  {
    icon: <SpeedIcon fontSize="large" color="primary" />,
    title: 'Real-time Processing',
    description: 'Get instant results from our optimized deep learning models, allowing for quick assessment and decision-making.'
  },
  {
    icon: <SchoolIcon fontSize="large" color="primary" />,
    title: 'Educational Tool',
    description: 'Perfect for students, researchers, and healthcare professionals to learn about AI applications in medical imaging.'
  }
];

const Home = () => {
  const { isAuthenticated } = useContext(AuthContext);
  
  return (
    <Box>
      {/* Hero Section */}
      <Box 
        sx={{ 
          backgroundColor: 'primary.main', 
          color: 'white',
          py: 8
        }}
      >
        <Container maxWidth="md">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={7}>
              <Typography variant="h3" component="h1" gutterBottom>
                Advanced Medical Image Analysis with Deep Learning
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, fontWeight: 'normal' }}>
                Upload X-ray images for instant AI-powered analysis, visualization, and diagnostic assistance
              </Typography>
              {isAuthenticated ? (
                <Button 
                  variant="contained" 
                  color="secondary" 
                  size="large"
                  component={RouterLink}
                  to="/analyze"
                  startIcon={<CloudUploadIcon />}
                >
                  Analyze an Image
                </Button>
              ) : (
                <Box>
                  <Button 
                    variant="contained" 
                    color="secondary" 
                    size="large"
                    component={RouterLink}
                    to="/register"
                    sx={{ mr: 2 }}
                  >
                    Get Started
                  </Button>
                  <Button 
                    variant="outlined" 
                    color="inherit" 
                    size="large"
                    component={RouterLink}
                    to="/login"
                  >
                    Log In
                  </Button>
                </Box>
              )}
            </Grid>
            <Grid item xs={12} md={5}>
              <Box 
                component="img"
                src="/static/hero-image.png"
                alt="AI analyzing a medical image"
                sx={{
                  width: '100%',
                  maxHeight: 300,
                  objectFit: 'contain',
                  display: { xs: 'none', md: 'block' }
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h4" component="h2" align="center" gutterBottom>
          Key Features
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 6 }}>
          Discover how our platform can help with medical image analysis
        </Typography>
        
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', p: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" align="center" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" align="center" color="text.secondary">
                  {feature.description}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
      
      {/* How It Works Section */}
      <Box sx={{ backgroundColor: '#f5f8fa', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" component="h2" align="center" gutterBottom>
            How It Works
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 6 }}>
            A simple three-step process to analyze your medical images
          </Typography>
          
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" color="primary" gutterBottom>1</Typography>
                  <Typography variant="h6" gutterBottom>Upload Your X-ray</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Simply upload your X-ray image through our user-friendly interface. We accept common formats like JPEG and PNG.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" color="primary" gutterBottom>2</Typography>
                  <Typography variant="h6" gutterBottom>AI Analysis</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Our deep learning models analyze the image, identifying potential abnormalities and generating visualizations.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" color="primary" gutterBottom>3</Typography>
                  <Typography variant="h6" gutterBottom>View Results</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Receive comprehensive results including classification, confidence scores, heatmaps, and segmentation masks.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <Box sx={{ textAlign: 'center', mt: 6 }}>
            {isAuthenticated ? (
              <Button 
                variant="contained" 
                size="large"
                component={RouterLink}
                to="/analyze"
              >
                Try It Now
              </Button>
            ) : (
              <Button 
                variant="contained" 
                size="large"
                component={RouterLink}
                to="/register"
              >
                Create Account
              </Button>
            )}
          </Box>
        </Container>
      </Box>
      
      {/* Disclaimer Section */}
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Card sx={{ p: 4, backgroundColor: '#f8f9fa' }}>
          <Typography variant="h6" gutterBottom>
            Educational Disclaimer
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary" paragraph>
            This application is designed for educational and demonstration purposes only. The analysis provided should not be used for clinical diagnosis or replace professional medical advice.
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            The deep learning models used in this application are trained on publicly available datasets and may not account for all possible conditions or variations in medical images. Always consult with qualified healthcare professionals for proper diagnosis and treatment.
          </Typography>
        </Card>
      </Container>
    </Box>
  );
};

export default Home; 