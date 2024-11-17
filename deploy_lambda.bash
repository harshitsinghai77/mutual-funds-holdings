#!/bin/bash

# Step 1: Define the new folder and zip file name
NEW_FOLDER="lambda_deployment_package"
ZIP_FILE="${NEW_FOLDER}.zip"
LAMBDA_FOLDER="lambda"  # The original source folder for lambda code

# Step 2: Create the new folder
echo "Creating folder: $NEW_FOLDER"
mkdir $NEW_FOLDER

# Step 3: Copy all files from lambda folder to the new folder
echo "Copying files from $LAMBDA_FOLDER to $NEW_FOLDER"
cp -r $LAMBDA_FOLDER/* $NEW_FOLDER/

# Step 4: Check if requirements.txt exists and install dependencies
if [ -f "$NEW_FOLDER/requirements.txt" ]; then
  echo "Found requirements.txt, installing dependencies..."
  pip install -r "$NEW_FOLDER/requirements.txt" -t "$NEW_FOLDER/"
  # pip install -r requirements.txt -t .
else
  echo "No requirements.txt found, skipping dependency installation."
fi

# Step 5: Zip the new folder
echo "Zipping the contents of $NEW_FOLDER into $ZIP_FILE"
zip -r $ZIP_FILE $NEW_FOLDER/*

# Step 6: Update CDK to use the zip file for Lambda code (Manually or dynamically edit the CDK app)
echo "Deploying using CDK..."

# Assuming you have CDK set up, you would trigger the deployment using the zip file.
# Make sure that your CDK code points to the correct zip file path, e.g., `code=_lambda.Code.from_asset('path/to/zip')`
# We can't directly alter the CDK code in this script, so ensure your CDK stack is already set to use $ZIP_FILE.

# This will deploy the Lambda function using the zip file you've created
cdk deploy

# Step 7: Clean up - remove the new folder and zip file
echo "Cleaning up: Deleting $NEW_FOLDER and $ZIP_FILE"
rm -rf $NEW_FOLDER
rm $ZIP_FILE

echo "Deployment and cleanup complete."
