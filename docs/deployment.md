# Deploying to AWS

This guide outlines the steps to deploy the Medical Image Analysis application to AWS infrastructure.

## Architecture Overview

The recommended AWS architecture consists of:

1. **Compute**: Amazon EC2 or ECS for running the containerized application
2. **Database**: Amazon RDS for PostgreSQL
3. **Storage**: Amazon S3 for storing images
4. **Networking**: Amazon VPC, Load Balancer, and Security Groups
5. **Domain & SSL**: Amazon Route 53 and Certificate Manager (optional)

## Deployment Steps

### 1. Set Up a VPC

Create a VPC with public and private subnets:

1. Navigate to the VPC service in the AWS console
2. Create a VPC with at least 2 public and 2 private subnets across different availability zones
3. Create an Internet Gateway and attach it to the VPC
4. Set up route tables for both public and private subnets

### 2. Set Up RDS Database

1. Navigate to the RDS service in the AWS console
2. Launch a PostgreSQL instance in the private subnets of your VPC
3. Configure security groups to allow connections from your application servers
4. Note the database endpoint, username, password, and database name

### 3. Set Up S3 Bucket for Image Storage

1. Navigate to the S3 service in the AWS console
2. Create a new bucket for storing medical images
3. Configure CORS settings to allow access from your application
4. Note the bucket name for configuration

### 4. Deploy the Application on EC2

#### Option 1: Using EC2 Directly

1. Launch an EC2 instance in a public subnet of your VPC
2. Install Docker on the instance
3. Clone the repository to the instance
4. Build and run the Docker container:
   ```
   docker build -t medical-image-analysis .
   docker run -p 80:8000 -e DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/dbname -e S3_BUCKET=your-bucket-name medical-image-analysis
   ```

#### Option 2: Using ECS with Fargate

1. Create an ECR repository and push your Docker image
2. Create an ECS cluster with Fargate
3. Define a task definition with your container configuration
4. Create a service to run your task definition
5. Set up an Application Load Balancer to route traffic to your service

### 5. Configure Environment Variables

Ensure your application is configured with the following environment variables:

- `DATABASE_URL`: The PostgreSQL connection string for your RDS instance
- `SECRET_KEY`: A secure random string for JWT token generation
- `S3_BUCKET`: The name of your S3 bucket for image storage
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: AWS credentials for S3 access

### 6. Set Up a Load Balancer (Optional)

For high availability:

1. Create an Application Load Balancer in your VPC
2. Configure target groups pointing to your EC2 instances or ECS service
3. Set up HTTPS listeners with certificates from ACM

### 7. Set Up Domain and SSL (Optional)

1. Register a domain in Route 53 or configure an existing domain
2. Request a certificate in ACM for your domain
3. Configure Route 53 to point to your load balancer

## Monitoring and Maintenance

1. Set up CloudWatch alarms for monitoring your EC2 instances, ECS services, and RDS database
2. Configure CloudWatch Logs for application logging
3. Set up regular backups of your RDS database
4. Implement an automated deployment pipeline using AWS CodePipeline or GitHub Actions

## Security Considerations

1. Use IAM roles with least privilege for your EC2 instances and ECS tasks
2. Keep all security groups as restrictive as possible
3. Enable encryption for your RDS database and S3 bucket
4. Regularly rotate passwords and access keys
5. Configure AWS WAF for additional protection against common web exploits

## Cost Optimization

1. Use reserved instances for EC2 and RDS to reduce costs for long-term deployments
2. Configure auto-scaling for EC2 instances based on demand
3. Monitor your S3 usage and implement lifecycle policies to move infrequently accessed data to cheaper storage tiers

## Troubleshooting

If you encounter issues:

1. Check security groups to ensure proper connectivity between components
2. Verify environment variables are correctly set
3. Check CloudWatch Logs for application errors
4. Test connectivity to the database and S3 bucket from the application server 