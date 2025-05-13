import React, { useState, useEffect, useContext } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  CircularProgress,
  Button,
  Alert,
  Divider,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import axios from 'axios';

import { AuthContext } from '../context/AuthContext';

const PredictionHistory = () => {
  const { token } = useContext(AuthContext);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  
  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await axios.get('/api/predictions/history', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        setPredictions(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching predictions:', err);
        setError('Error fetching prediction history. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchPredictions();
  }, [token]);
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  const handleOpenDialog = (prediction) => {
    setSelectedPrediction(prediction);
    setDialogOpen(true);
  };
  
  const handleCloseDialog = () => {
    setDialogOpen(false);
  };
  
  const getConfidenceChip = (confidence) => {
    let color = 'success';
    if (confidence < 0.7) color = 'warning';
    if (confidence < 0.5) color = 'error';
    
    return (
      <Chip 
        label={`${Math.round(confidence * 100)}%`}
        size="small"
        color={color}
      />
    );
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Prediction History
        </Typography>
        <Typography variant="body1" color="text.secondary">
          View your past medical image analyses
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ width: '100%', mb: 4 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : predictions.length > 0 ? (
          <>
            <TableContainer>
              <Table sx={{ minWidth: 650 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Diagnosis</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {predictions
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((prediction) => (
                      <TableRow key={prediction.id} hover>
                        <TableCell>{formatDate(prediction.created_at)}</TableCell>
                        <TableCell>
                          <Chip 
                            label={prediction.prediction_result}
                            color={prediction.prediction_result === 'Normal' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{getConfidenceChip(prediction.confidence_score)}</TableCell>
                        <TableCell>
                          <Button
                            variant="text"
                            size="small"
                            startIcon={<VisibilityIcon />}
                            onClick={() => handleOpenDialog(prediction)}
                          >
                            View Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={predictions.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        ) : (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <AnalyticsIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" paragraph>
              No prediction history found.
            </Typography>
            <Button
              variant="contained"
              component={RouterLink}
              to="/analyze"
            >
              Analyze an Image
            </Button>
          </Box>
        )}
      </Paper>
      
      {/* Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedPrediction && (
          <>
            <DialogTitle>
              Prediction Details
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  Diagnosis: {selectedPrediction.prediction_result}
                </Typography>
                <Typography variant="body2">
                  Confidence: {Math.round(selectedPrediction.confidence_score * 100)}%
                </Typography>
                <Typography variant="body2">
                  Date: {formatDate(selectedPrediction.created_at)}
                </Typography>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={3}>
                {selectedPrediction.heatmap_path && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Heatmap Visualization
                    </Typography>
                    <img 
                      src={`/static/images/heatmaps/${selectedPrediction.heatmap_path.split('/').pop()}`} 
                      alt="Heatmap" 
                      style={{ width: '100%', borderRadius: '8px' }}
                    />
                  </Grid>
                )}
                
                {selectedPrediction.segmentation_path && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Segmentation Mask
                    </Typography>
                    <img 
                      src={`/static/images/segmentations/${selectedPrediction.segmentation_path.split('/').pop()}`} 
                      alt="Segmentation" 
                      style={{ width: '100%', borderRadius: '8px' }}
                    />
                  </Grid>
                )}
                
                {!selectedPrediction.segmentation_path && selectedPrediction.prediction_result !== 'Normal' && (
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, bgcolor: '#f5f8fa' }}>
                      <Typography variant="body2">
                        Segmentation mask not available for this prediction.
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default PredictionHistory; 