# DEFINE THE GLOBAL VARIABLES
export BUCKET_NAME="semantic-job-search-bucket"
export STACK_NAME="semantic-job-search-stack"

# Check if the deployment.zip file size is less than 50MB
if [ $(stat -c%s "packaged/deployment.zip") -gt 52428800 ]; then
    echo "The deployment.zip file is greater than 50MB. Please reduce the size of the deployment.zip file and try again."
    exit 1
fi

# CHECK IF THE BUCKET EXISTS
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'
then
    echo "The Bucket $BUCKET_NAME does not exist"
    echo "Creating Bucket $BUCKET_NAME Now!"
    aws s3 mb s3://$BUCKET_NAME
else
    echo "Bucket exists"
fi

# PACKAGE AND DEPLOY THE CLOUDFORMATION TEMPLATE
aws cloudformation package --template-file packaged/sam.json --s3-bucket $BUCKET_NAME --output-template-file packaged/sam-packaged.yaml
aws cloudformation deploy --template-file packaged/sam-packaged.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_IAM
