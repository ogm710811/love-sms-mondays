pipeline {
  agent any
  environment {
    AWS_DEFAULT_REGION = 'us-east-2'
    IS_PR      = "${env.CHANGE_ID ?: ''}"
    STACK_NAME = "${env.CHANGE_ID ? "love-sms-pr-${env.CHANGE_ID}" : "love-sms-mondays"}"
    ENV_SUFFIX = "${env.CHANGE_ID ? "pr-${env.CHANGE_ID}" : ""}"
    ARTIFACT_BUCKET = 'ogm-artifacts'                // <-- create this S3 bucket once
    ARTIFACT_KEY = "builds/love-sms-${env.BUILD_NUMBER}.zip"
    PHONE_NUMBER = credentials('WIFE_PHONE_E164')    // Jenkins string credential e.g. +19045551234
    API_URL = 'https://api.quotable.io/random'       // change as needed
    API_KEY_PARAM = ''                               // e.g., /apps/love/apiKey (optional)
  }
  options {
    timestamps()
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build Lambda Zip') {
      steps {
        sh '''
          rm -f love-sms.zip
          python3 -m pip install --upgrade pip
          python3 -m pip install --target package -r requirements.txt
          (cd package && zip -r ../love-sms.zip .)
          zip -g love-sms.zip app.py
        '''
      }
    }
    stage('Upload Artifact') {
      steps { sh "aws s3 cp love-sms.zip s3://${ARTIFACT_BUCKET}/${ARTIFACT_KEY}" }
    }
    stage('Preview Deploy (PR only)') {
      when { expression { return env.CHANGE_ID as boolean } }
      environment {
        ENV_SUFFIX = "pr-${env.CHANGE_ID}"
        STACK_NAME = "love-sms-pr-${env.CHANGE_ID}"
      }
      steps {
        sh """
          aws cloudformation deploy \
            --stack-name ${STACK_NAME} \
            --template-file template.yaml \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameter-overrides \
              EnvSuffix=${ENV_SUFFIX} \
              ArtifactBucket=${ARTIFACT_BUCKET} \
              ArtifactKey=${ARTIFACT_KEY} \
              PhoneNumber=${PHONE_NUMBER} \
              TimeZone=America/New_York \
              ApiUrl='${API_URL}' \
              ApiKeyParameterName='${API_KEY_PARAM}' \
            --tags Project=love-sms PullRequest=${CHANGE_ID}
        """
      }
    }
    stage('Deploy CloudFormation (main only)') {
      when { branch 'main' }   // or: when { expression { return !env.CHANGE_ID } }
      steps {
        sh """
          aws cloudformation deploy \
            --stack-name ${STACK_NAME} \
            --template-file template.yaml \
            --capabilities CAPABILITY_NAMED_IAM \
            --no-fail-on-empty-changeset \
            --parameter-overrides \
              ArtifactBucket=${ARTIFACT_BUCKET} \
              ArtifactKey=${ARTIFACT_KEY} \
              PhoneNumber=${PHONE_NUMBER} \
              TimeZone=America/New_York \
              ApiUrl='${API_URL}' \
              ApiKeyParameterName='${API_KEY_PARAM}' \
              EnvSuffix=''
        """
      }
    }
    stage('Smoke Test (invoke once)') {
      steps {
        sh """
          LAMBDA_NAME=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} \
            --query "Stacks[0].Outputs[?OutputKey=='LambdaName'].OutputValue" --output text)
          aws lambda invoke --function-name "$LAMBDA_NAME" out.json
          cat out.json
        """
      }
    }
  }
}