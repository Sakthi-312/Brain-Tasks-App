import subprocess
import boto3

CLUSTER_NAME = "Brain-cluster"
REGION = "ap-south-1"
DEPLOYMENT_FILE = "/tmp/deployment.yaml"
SERVICE_FILE = "/tmp/service.yaml"

def run(cmd):
    print("Running:", cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode

def lambda_handler(event, context):

    # Step 1: Download kubectl
    run("curl -o /tmp/kubectl https://amazon-eks.s3.amazonaws.com/1.29.0/2024-01-04/bin/linux/amd64/kubectl")
    run("chmod +x /tmp/kubectl")

    # Step 2: Update kubeconfig
    run(f"/tmp/kubectl version --client")
    run(f"aws eks update-kubeconfig --region {REGION} --name {CLUSTER_NAME}")

    # Step 3: Download YAML files from CodePipeline artifact (S3)
    s3 = boto3.client("s3")
    artifact_bucket = event["CodePipeline.job"]["data"]["inputArtifacts"][0]["location"]["s3Location"]["bucketName"]
    artifact_key = event["CodePipeline.job"]["data"]["inputArtifacts"][0]["location"]["s3Location"]["objectKey"]

    s3.download_file(artifact_bucket, artifact_key + "/deployment.yaml", DEPLOYMENT_FILE)
    s3.download_file(artifact_bucket, artifact_key + "/service.yaml", SERVICE_FILE)

    # Step 4: Apply Kubernetes manifests
    run(f"/tmp/kubectl apply -f {DEPLOYMENT_FILE}")
    run(f"/tmp/kubectl apply -f {SERVICE_FILE}")

    # Step 5: Report success back to CodePipeline
    codepipeline = boto3.client("codepipeline")
    job_id = event["CodePipeline.job"]["id"]
    codepipeline.put_job_success_result(jobId=job_id)

    return "Deployment Completed"
