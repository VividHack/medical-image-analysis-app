import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class MedicalImageClassifier(nn.Module):
    def __init__(self, num_classes=2, pretrained=True):
        super(MedicalImageClassifier, self).__init__()
        
        # Load a pre-trained ResNet-50 model
        self.resnet = models.resnet50(weights='IMAGENET1K_V1' if pretrained else None)
        
        # Replace the final fully connected layer to match our number of classes
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.resnet(x)
    
    def monte_carlo_inference(self, x, num_samples=10):
        """
        Perform Monte Carlo dropout inference for uncertainty estimation
        """
        self.train()  # Enable dropout
        
        outputs = []
        for _ in range(num_samples):
            with torch.no_grad():
                output = self.forward(x)
                outputs.append(F.softmax(output, dim=1))
        
        # Stack outputs to calculate mean and variance
        outputs = torch.stack(outputs)
        mean_output = outputs.mean(dim=0)
        var_output = outputs.var(dim=0)
        
        # Switch back to eval mode
        self.eval()
        
        return mean_output, var_output
    
    def predict_with_uncertainty(self, x, num_samples=10):
        """
        Get predictions with uncertainty estimates
        """
        mean_probs, var_probs = self.monte_carlo_inference(x, num_samples)
        
        # Get predicted class
        pred_class = torch.argmax(mean_probs, dim=1)
        
        # Get confidence score (probability of predicted class)
        confidence = mean_probs.gather(1, pred_class.unsqueeze(1)).squeeze(1)
        
        # Get uncertainty (variance of predicted class)
        uncertainty = var_probs.gather(1, pred_class.unsqueeze(1)).squeeze(1)
        
        return pred_class, confidence, uncertainty
    
    def get_gradcam_layer(self):
        """
        Return the layer name to use for Grad-CAM
        """
        return "resnet.layer4.2"

# Function to load trained model
def load_model(model_path, device, num_classes=2):
    model = MedicalImageClassifier(num_classes=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model 