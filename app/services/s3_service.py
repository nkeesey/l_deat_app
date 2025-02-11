import boto3
import pandas as pd
from io import StringIO
import os

class S3Service: 
    def __init__(self, use_local=True, data_dir='data'):
        """
        Initialize the S3 service, local = CSV, remote = S3
        """
        self.use_local = use_local
        self.data_dir = data_dir

        if not self.use_local:
            self.s3_client  = boto3.client(
                's3',
                aws_access_key_id = 'TBD',
                aws_secret_access_key = 'TBD',
                region_name = 'TBD'
            )

    def get_file(self, filename, bucket=None):
        """
        Retrieve file from S3 bucket, or local data directory

        Args:
            filename (str): name of local file to retrieve
            bucket (str): name of S3 bucket to retrieve if not local
        """
        try:
            if self.use_local:
                file_path = os.path.join(self.data_dir, filename)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {filename} not found in {self.data_dir}")
                return pd.read_csv(file_path)
            else:
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                file_content = response['Body'].read().decode('utf-8')
                return pd.read_csv(StringIO(file_content))
        except Exception as e:
            raise Exception(f"Error retrieving file: {str(e)}")
    
    def list_files(self, bucket=None, prefix=''):
        """
        List all files in a bucket (or local data directory) with given prefix
        """
        try:
            if self.use_local:
                files = []
                for file in os.listdir(self.data_dir):
                    if file.endswith('.csv'):
                        files.append(file)
                return files
            else:
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix
                )
                return [item['Key'] for item in response.get('Contents', [])]
        except Exception as e:
            raise Exception(f"Error listing files: {str(e)}")
        