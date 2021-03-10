from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import boto3
import botocore
from botocore.exceptions import ClientError
import logging
import json
import random
import decimal


#****************************************
#S3 methods
#****************************************
def getS3object(object_name):
    """
    Download a file form selected bucket
    """
    s3 = boto3.resource('s3')
    
    bucket_name = "danbeck.blackjack"

    try:
        s3.Bucket(bucket_name).download_file(object_name, "{0}".format(object_name))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
