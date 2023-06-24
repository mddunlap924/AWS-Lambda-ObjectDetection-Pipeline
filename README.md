# Introduction

![ObjDetGIF](https://github.com/mddunlap924/AWS-Lambda-ObjectDetection-Pipeline/blob/main/imgs/ColumbusCircle_YOLOV5.gif)

This application performs image analysis/object detection on [EarthCam images from Columbus Circle, NY](https://www.earthcam.com/usa/newyork/columbuscircle/?cam=columbus_circle). Each day the application will analyze a set of images stored on EarthCam’s website. During the analysis certain objects such as people, cars, buses, etc. are counted for each image by using YOLOv5. The sum of objects for all images, by day, are incorporated into a database and data visualizations are created. The application is deployed using AWS services.

Some of the key aspects and functions of this application are:

- **Web scraping** using [Selenium](https://www.selenium.dev/) with a Headless Chrome Webdriver
- **Object Detection** using [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5)
- **Data Visualization and Analytics** using [Ploty](https://plotly.com/)
- **AWS Deployment** using services such as [Docker,](https://www.docker.com/) [AWS Lambda](https://aws.amazon.com/lambda/), [Elastic Container Registry (ECR](https://aws.amazon.com/ecr/)), [EventBridge](https://aws.amazon.com/eventbridge/), and [Simple Storage Service (S3)](https://aws.amazon.com/s3/)

# Results

For this application there are two different interactive data visualizations created using Ploty and are being hosted on S3 buckets set as static websites. Click the links below to visit the interactive graphs which are updated daily around 5pm ET.

[Active Web Page Link - EarthCam Image Analyzed Daily with YoloV5 Nano](https://aws-columbus-circle-img.s3.us-east-2.amazonaws.com/index.html)

[Active Web Page Link - Line Chart of Counted Objects using YOLOv5 vs. Date](https://aws-columbus-circle.s3.us-east-2.amazonaws.com/index.html)

# AWS Deployment Architecture

Transitioning between a local model and functional code to a deployed application has a number of considerations. With the advent of cloud computing services like [Amazon Web Services (AWS)](https://aws.amazon.com/what-is-aws/), [Microsoft Azure](https://azure.microsoft.com/en-us/), and [Google Cloud Platform](https://cloud.google.com/) it has become easier to deploy applications. In this application AWS services are utilized and the cloud architecture shown in the below image is implemented for deployment. Also, for each of these services AWS best practices were incorporated.

<p align="center">
  <img width="600" height="400" src="https://github.com/mddunlap924/AWS-Lambda-ObjectDetection-Pipeline/blob/main/imgs/AWS_Lambda_EarthCam.drawio.png">
</p>

The AWS architecture functions as follows:

- First, the application is developed and tested locally. Once the application is functioning correctly, a Docker image is built as shown in the [Dockerfile](https://github.com/mddunlap924/AWS-Lambda-ObjectDetection-Pipeline/blob/main/Dockerfile).
  - Please note that the Docker image cannot be any Docker image but must adhere to the AWS Lambda Python docker image which can be found on [Docker Hub](https://hub.docker.com/r/amazon/aws-lambda-python). 

- The Docker image is also test locally using the [AWS Lambda Runtime Interface Emulator](https://github.com/aws/aws-lambda-runtime-interface-emulator). This is a very helpful features because it lets you determine max memory used and provides an estimate on the runtime for the image. Both of these values will need to be accounted for when deploying on AWS.
- The Docker image is pushed to an AWS Elastic Container Registry (ECR) and this can be used to store several Docker images and called upon by other AWS services for deployment.
- An AWS Lambda function was created and this links to the Docker image previously stored in the ECR. AWS Lambda services are serverless and event-driven compute resources. You only pay for what you use with this service. This function performs the majority of the work for this application.
- A total of three S3 buckets were setup.
  - The first bucket (as shown in the center most bucket in the above figure) stores YOLOv5 Nano model weights and the database for plotting the line chart shown earlier. This database is read from the S3 bucket by the Lambda function, updated with results each day, and then written back to the bucket.
  - The other two buckets are static websites that are used to display the interactive Ploty graphs shown in the Results section. The Lambda function writes the updated HTML to each of these buckets when its invoked each day.
    - If you experience issues getting and putting objects from the S3 buckets then start by looking at your Lambda function’s IAM Role and/or the S3 bucket policy. 

  - Lastly, an AWS EventBridge service was setup to trigger the AWS Lambda function each day at a given time. This was setup using a cron expression and any errors are logged with [CloudWatch](https://aws.amazon.com/cloudwatch/).


Serverless and event-driven compute resources like AWS Lambda are a great choice for this application because the application only needs to execute for a few seconds once a day. Also, you only pay for what you use with AWS Lambda and with this application’s relatively low compute usage it can fall within the AWS free tier or it only costs a few cents per month. 
