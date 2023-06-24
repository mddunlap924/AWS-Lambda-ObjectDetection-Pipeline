import os
from countobjects.aws_s3_interactions import AWSBucketS3
from countobjects.webscraper import EarthCamImg
from countobjects.objdet import obj_det_update
from awsplots import plotly_to_s3
import boto3
import shutil

""" 
AWS Best Practices
- Connect to S3 buckets once
- Store S3 bucket names in environment variables. Locally this code was developed in a virtual environment in 
PyCharm and the environment variables were set in PyCharm to the S3 bucket names. The same environment variables were 
setup for the AWS Lambda function as well.
"""

# AWS Lambda functions can only write to /tmp directory but the "/" syntax is not required for local development.
# This logic is added to establish variables for local dev. or docker/Lambda prod.
if 'home' in os.getcwd():
    TMP_DIR = 'tmp/'    # Local syntax for development
else:
    TMP_DIR = '/tmp/'  # AWS Lambda syntax for Docker Container

# https://towardsdatascience.com/working-with-amazon-s3-buckets-with-boto3-785252ea22e0
s3 = boto3.client('s3')

# YoloV5 Tips and Tricks for running AWS Lambda functions (i.e. need to change default disk writes)
# https://github.com/ultralytics/yolov5/pull/4727
# https://github.com/ultralytics/yolov5/blob/master/utils/general.py (see def user_config_dir)
os.environ['YOLOV5_CONFIG_DIR'] = '/tmp'  # AWS Lambda can only write to /tmp directory


def handler(event, context):
    """ AWS Lambda will execute this method """
    print('main.py "handler" method has started')
    print(f'Current Working Directory {os.getcwd()}')

    # Download images to local disk from EarthCam
    earth_cam = EarthCamImg(save_dir=TMP_DIR)
    earth_cam.get_imgs_store_on_disk()

    # Move YoloV5 model weights from S3 bucket to /tmp directory
    s3.download_file(Bucket=os.environ['S3_DATA_BUCKET_NAME'],
                     Key=os.environ['YOLO_WEIGHTS'],
                     Filename=TMP_DIR + os.environ['YOLO_WEIGHTS'])

    # Read Current CSV in S3 Bucket
    s3_data_bucket = AWSBucketS3(s3=s3, bucket=os.environ['S3_DATA_BUCKET_NAME'])
    df_disk = s3_data_bucket.read_csv_on_s3(filename=os.environ['DB_FILENAME'])

    # Count Objects in Images and Append to Current Database
    df = obj_det_update(tmp_dir=TMP_DIR, df_disk=df_disk, s3_data=s3_data_bucket)

    # Upload the Updated Database to S3 Bucket
    s3_data_bucket.write_csv_to_s3(filename=os.environ['DB_FILENAME'], df=df)

    # Create Plotly Figure and save an HTML object in S3 Bucket hosted as website
    line_fig = plotly_to_s3.create_plotly_line_fig(df=df)
    img_fig = plotly_to_s3.create_plotly_img_fig(tmp_dir=TMP_DIR)

    # Write Plotly HTML files to S3 Bucket Websites
    for bucket, fig in [('S3_HTML_LINE', line_fig), ('S3_HTML_IMG', img_fig)]:
        plotly_to_s3.upload_html_to_s3(tmp_dir=TMP_DIR, s3=s3, bucket=os.environ[bucket], fig=fig)

    # Delete All Files from the Temporary Directory
    for files in os.listdir(TMP_DIR):
        path = os.path.join(TMP_DIR, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

    print('End of Handler Method')
    return


"""
Test your AWS Lambda function locally using the following commands:
https://docs.aws.amazon.com/lambda/latest/dg/images-create.html
Runtime Interface Emulator - https://docs.aws.amazon.com/lambda/latest/dg/images-test.html

1) docker build -t appname .
2) docker run -p 9000:8080 appname
3) curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

Note: for line 2 a bash script can also be written to pass environment variables into the Docker image for local testing
"""

if __name__ == '__main__':
    handler('event', 'context')

