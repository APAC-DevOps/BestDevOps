# Q-CTRL HAVE TO HIRE JIANHUA

Set up a website with CloudFront + S3 Bucket

## Pre-requisite

- Python3.6 or higher
- boto3
- access key & secret key of an AWS IAM user with Admin permission
- basic AWS knowledge

## Environment Setup On Linux or Mac
`type “aws configure” in your terminal`
`create a s3 bucket, and upload the file trimed-cloudfront-s3-static-site.json to the created s3 bucket`
`copy the s3 bucket url from AWS web console, and replace the line 33 in the hire-jianhua.py`


## Launch Your Web Site
`python3 hire-jianhua.py --Env Dev --Ref jianhua`
`upload the file “index.html” to the s3 bucket created by running the command above`
`# you can find the name of S3 bucket from the “resource” tab of the relevant stack in AWS cloudformation web console`

## Test
`copy the dns name of your cloudFront from AWS CloudFront web console`
`paste the copied DNS name into your browser and hit.`

## Know Issues
`# Due to AWS’s internal issue, after launching and deploying your website, you might not be able to access the deployed website immediately. Something you might need to wait up to hours before your website accessible.`
