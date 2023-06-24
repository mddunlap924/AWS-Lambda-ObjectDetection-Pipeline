import boto3
import pandas as pd
import io


class AWSBucketS3:
    """ Class for Reading and Writing CSV Files to an AWS S3 Bucket """

    def __init__(self, s3, bucket):
        self.s3 = s3,
        self.s3 = self.s3[0]
        self.bucket = bucket

    def read_csv_on_s3(self, filename):
        """ Read file from AWS S3 Bucket """
        # Download existing file from S3
        # https://towardsdatascience.com/reading-and-writing-files-from-to-amazon-s3-with-pandas-ccaf90bfe86c
        response = self.s3.get_object(Bucket=self.bucket,
                                      Key=filename)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 200:
            print(f"Successful S3 get_object response. Status - {status}")
            df = pd.read_csv(response.get("Body"))
            print(f'Read {filename} from AWS S3 {self.bucket}')
            return df
        else:
            print(f"Unsuccessful S3 get_object response. Status - {status}")
            return False

    def write_csv_to_s3(self, filename, df):
        """ Write file to AWS S3 Bucket """

        # Writing file to csv
        with io.StringIO() as csv_buffer:
            df.to_csv(csv_buffer, index=False)

            response = self.s3.put_object(Bucket=self.bucket,
                                          Key=filename,
                                          Body=csv_buffer.getvalue(),
                                          )

            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

            if status == 200:
                print(f"Successful S3 put_object response. Status - {status}: {filename} on {self.bucket}")
            else:
                print(f"Unsuccessful S3 put_object response. Status - {status}")
