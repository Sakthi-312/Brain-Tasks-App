Brain Tasks App – CI/CD Deployment (Docker, ECR, EKS, CodePipeline, Lambda):

This project deploys a React application to AWS using
Docker → ECR → EKS → CodePipeline → Lambda → kubectl.

1. Install Required Tools

Install Git

Install Docker

Install AWS CLI

Fork & clone repository:

    git clone https://github.com/Vennilavan12/Brain-Tasks-App.git
    cd Brain-Tasks-App/dist

2. Create Dockerfile

Inside dist/:

    FROM nginx:latest
    COPY ./dist /usr/share/nginx/html
    EXPOSE 3000
    CMD ["nginx", "-g", "daemon off;"]

Build & Run Docker Image

    docker build -t brain-task .
    docker run -d -p 3000:80 brain-task

3. Push Image to AWS ECR

Create ECR Repo

    aws ecr create-repository --repository-name brain-task-app-repo --region ap-south-1

Login to ECR

    aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

Tag & Push Image

    docker tag brain-task:latest <ACCOUNT>.dkr.ecr.ap-south-1.amazonaws.com/brain-task-app-repo:latest
    docker push <ACCOUNT>.dkr.ecr.ap-south-1.amazonaws.com/brain-task-app-repo:latest

4. Create EKS Cluster

    eksctl create cluster --name Brain-cluster --region ap-south-1 --node-type t2.small --nodes 1

Confirm Cluster
    
    kubectl get nodes

5. Kubernetes Deployment

Create:

  deployment.yaml

  service.yaml

Apply them:

    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml

Check LoadBalancer:

    kubectl get svc

6. Push Code to GitHub

    git add .
    git commit -m "Initial CI/CD setup"
    git remote set-url origin https://<username>:<token>@github.com/<username>/Brain-Tasks-App.git
    git push origin main

7. Create CodeBuild Project

1. Source: GitHub
2. Environment: Ubuntu / Amazon Linux
3. IAM role: allow S3 + ECR + CloudWatch
4. Add buildspec.yml:

    version: 0.2
    
    phases:
      install:
        commands:
          - echo "Build step running"
    
    artifacts:
      files:
        - '**/*'

8. Create CodePipeline

Stages:
  1. Source – GitHub
  2. Build – CodeBuild
  3. Deploy – Lambda (Custom Action)

9. Lambda Deploy to EKS

Lambda responsibilities:

  1. Download kubectl
  2. Update kubeconfig
  3. Read YAML files from CodePipeline S3 artifact
  4. Apply manifests to EKS using kubectl
  5. Send success result back to CodePipeline

Required IAM Permissions:

  1. EKS access
  2. S3 read permissions
  3. CodePipeline success callback

10. Fix RBAC (If Required)

  If CodeBuild fails with authentication error:

    kubectl edit configmap aws-auth -n kube-system

  Add:

    - rolearn: arn:aws:iam::<ACCOUNT>:role/codebuild-service-role
      username: codebuild
      groups:
        - system:masters

11. Monitoring

Use AWS CloudWatch for:

  1. CodeBuild logs
  2. CodePipeline execution logs
  3. Lambda execution logs
  4. EKS pod & service logs

12. Cleanup (Optional)

    eksctl delete cluster --name Brain-cluster

Deployment Flow Summary:

    React App → Docker → ECR → EKS → CodePipeline → Lambda → kubectl apply
