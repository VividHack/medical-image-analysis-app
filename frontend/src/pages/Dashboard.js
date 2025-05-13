import React, { useContext, useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Paper,
  Divider,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar
} from '@mui/material';
import AddPhotoAlternateIcon from '@mui/icons-material/AddPhotoAlternate';
import HistoryIcon from '@mui/icons-material/History';
import MedicalInformationIcon from '@mui/icons-material/MedicalInformation';
import ArticleIcon from '@mui/icons-material/Article';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

import { AuthContext } from '../context/AuthContext';

const Dashboard = () => {
  const { user, token } = useContext(AuthContext);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    normalCount: 0,
    abnormalCount: 0
  });
  
  useEffect(() => {
    const fetchRecentPredictions = async () => {
      try {
        const response = await axios.get('/api/predictions/history', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const predictions = response.data;
        setRecentPredictions(predictions.slice(0, 5)); // Get latest 5
        
        // Calculate stats
        const totalAnalyses = predictions.length;
        const normalCount = predictions.filter(p => p.prediction_result === 'Normal').length;
        const abnormalCount = totalAnalyses - normalCount;
        
        setStats({
          totalAnalyses,
          normalCount,
          abnormalCount
        });
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching predictions:', error);
        setLoading(false);
      }
    };
    
    fetchRecentPredictions();
  }, [token]);
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back, {user?.username}! Here's your medical imaging analysis overview.
        </Typography>
      </Box>
      
      {/* Quick Actions */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="contained"
              fullWidth
              component={RouterLink}
              to="/analyze"
              startIcon={<AddPhotoAlternateIcon />}
              sx={{ py: 2 }}
            >
              Analyze New Image
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="outlined"
              fullWidth
              component={RouterLink}
              to="/history"
              startIcon={<HistoryIcon />}
              sx={{ py: 2 }}
            >
              View History
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="outlined"
              fullWidth
              color="secondary"
              component="a"
              href="https://www.nih.gov/news-events/news-releases/nih-clinical-center-provides-one-largest-publicly-available-chest-x-ray-datasets-scientific-community"
              target="_blank"
              rel="noopener noreferrer"
              startIcon={<ArticleIcon />}
              sx={{ py: 2 }}
            >
              Learn About Dataset
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      {/* Stats Overview */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h6" gutterBottom>
          Your Statistics
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%', bgcolor: 'primary.light', color: 'white' }}>
                <CardContent>
                  <Typography variant="h3" gutterBottom>
                    {stats.totalAnalyses}
                  </Typography>
                  <Typography variant="body1">
                    Total Analyses
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', bgcolor: '#4caf50', color: 'white' }}>
                <CardContent>
                  <Typography variant="h3" gutterBottom>
                    {stats.normalCount}
                  </Typography>
                  <Typography variant="body1">
                    Normal Results
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', bgcolor: '#f44336', color: 'white' }}>
                <CardContent>
                  <Typography variant="h3" gutterBottom>
                    {stats.abnormalCount}
                  </Typography>
                  <Typography variant="body1">
                    Abnormal Results
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Box>
      
      {/* Recent Activity */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        
        <Paper sx={{ p: 0 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : recentPredictions.length > 0 ? (
            <List>
              {recentPredictions.map((prediction, index) => (
                <React.Fragment key={prediction.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: prediction.prediction_result === 'Normal' ? '#4caf50' : '#f44336' }}>
                        {prediction.prediction_result === 'Normal' ? <CheckCircleIcon /> : <ErrorIcon />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="subtitle1" fontWeight="bold">
                          {prediction.prediction_result}
                        </Typography>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" color="text.secondary">
                            Confidence: {Math.round(prediction.confidence_score * 100)}%
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(prediction.created_at).toLocaleString()}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  {index < recentPredictions.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <MedicalInformationIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography color="text.secondary">
                No analyses performed yet. Start by analyzing a medical image.
              </Typography>
              <Button
                variant="contained"
                component={RouterLink}
                to="/analyze"
                sx={{ mt: 2 }}
              >
                Analyze Image
              </Button>
            </Box>
          )}
        </Paper>
      </Box>
      
      {/* Educational Note */}
      <Paper sx={{ p: 3, bgcolor: '#f8f9fa' }}>
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Educational Note
        </Typography>
        <Typography variant="body2" paragraph>
          This application uses deep learning to analyze chest X-rays for conditions like pneumonia. 
          The classification model is trained using transfer learning on a ResNet-50 architecture, 
          which has been fine-tuned on the NIH ChestX-ray14 dataset.
        </Typography>
        <Typography variant="body2">
          For visualization, we use Grad-CAM (Gradient-weighted Class Activation Mapping) to highlight 
          regions that significantly influence the model's predictions, making the AI decision-making process 
          more transparent and interpretable.
        </Typography>
      </Paper>
    </Container>
  );
};

export default Dashboard; 