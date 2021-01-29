import boto3
from datetime import datetime
import random
from botocore.exceptions import ClientError
import logging
import botocore

#****************************************
#           Global Variables
#****************************************
username = "danbeck"
now = datetime.now()

#****************************************
#1st level Functions/Methods for the code
#****************************************
def gen_6_digit_random_number():
    """Generates 6 digit random number"""
    gen_num = random.randint(1, 999999)
    return gen_num
    
def count_bucket_list(bucket_list):
    count = 0
    for i in bucket_list:
        count = count+1
    return count

def gen_bucket_list():
    """Generates lists buckets"""
    # Create an S3 client
    s3 = boto3.client('s3')
    # Call S3 to list current buckets
    response = s3.list_buckets()
    # Get a list of all bucket names from the response
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    # Print out the bucket list
    #print("Bucket List: %s" % buckets)
    return buckets
    
#****************************************
#2nd level Functions/Methods for the code
#****************************************
def list_all_buckets():
    """List all current buckets in S3"""
    new_bucket_list = gen_bucket_list()
    count = 1
    #for bucket in response['Buckets']:
        #print ('\t' + count + ':' + bucket['Name'])
        
    for i in new_bucket_list:
        print ("\t{0}: {1}".format(count,i))
        count = count+1
        
def create_bucket_setup(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return print("Error creating bucket {0}!".format(bucket_name))
    return print("Bucket {0} has been created.".format(bucket_name))
        
def put_object(dest_bucket_name):
    """Add an object to an Amazon S3 bucket

    The src_data argument must be of type bytes or a string that references
    a file specification.

    :param dest_bucket_name: string
    :param dest_object_name: string
    :param src_data: bytes of data or string reference to file spec
    :return: True if src_data was added to dest_bucket/dest_object, otherwise
    False
    """

    # object name
    dest_object_name = 'InsertedFile'
    
    # Path to file
    src_data = '/logo'
    
    # Construct Body= parameter
    if isinstance(src_data, bytes):
        object_data = src_data
    elif isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            logging.error(e)
            return print("Error at isinstance : FileNotFoundError/IOError exception")
    else:
        logging.error('Type of ' + str(type(src_data)) +
                      ' for the argument \'src_data\' is not supported.')
        return print("Error at else: isinstance")

    # Put the object
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=dest_bucket_name, Key=dest_object_name, Body=object_data)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        logging.error(e)
        return print("Error at put_object")
    finally:
        if isinstance(src_data, str):
            object_data.close()
    return print("File has been uploaded successfully")
    
def delete_object(bucket_name, object_name):
    """Delete an object from an S3 bucket

    :param bucket_name: string
    :param object_name: string
    :return: True if the referenced object was deleted, otherwise False
    """

    # Delete the object
    s3 = boto3.client('s3')
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_name)
    except ClientError as e:
        logging.error(e)
        return print("Error deleteing object from bucket!")
    return print("Object {0} deleted from {1}".format(object_name, bucket_name))
    
def delete_bucket_setup(bucket_name):
    """Delete an empty S3 bucket

    If the bucket is not empty, the operation fails.

    :param bucket_name: string
    :return: True if the referenced bucket was deleted, otherwise False
    """

    # Delete the bucket
    s3 = boto3.client('s3')
    try:
        s3.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return print("Error in delete bucket!")
    return print("Bucket {0} has been deleted!".format(bucket_name))
    
def copy_object(src_bucket_name, src_object_name, dest_bucket_name, dest_object_name=None):
    """Copy an Amazon S3 bucket object

    :param src_bucket_name: string
    :param src_object_name: string
    :param dest_bucket_name: string. Must already exist.
    :param dest_object_name: string. If dest bucket/object exists, it is
    overwritten. Default: src_object_name
    :return: True if object was copied, otherwise False
    """

    # Construct source bucket/object parameter
    copy_source = {'Bucket': src_bucket_name, 'Key': src_object_name}
    if dest_object_name is None:
        dest_object_name = src_object_name

    # Copy the object
    s3 = boto3.client('s3')
    try:
        s3.copy_object(CopySource=copy_source, Bucket=dest_bucket_name,
                       Key=dest_object_name)
    except ClientError as e:
        logging.error(e)
        return print("Error in copying object")
    return print("\n{1} from {0} was copied to {2} as {3}".format(src_bucket_name, 
                            src_object_name, dest_bucket_name, dest_object_name))
                            
def download_from_bucket_setup(bucket_name, file_to_download, new_file_name):
    """
    Download a file form selected bucket
    """
    s3 = boto3.resource('s3')

    try:
        s3.Bucket(bucket_name).download_file(file_to_download, "{0}.jpg".format(new_file_name))
        print("File {1} has been downloaded from {0}".format(bucket_name, file_to_download))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    
#****************************************
#3rd level Functions/Methods for the code
#****************************************
def create_bucket():
    """
    Create an S3 bucket
    """
    #Import generated number
    end_num = gen_6_digit_random_number()
    
    #generate bucket name
    bucket_name = "{0}-{1}".format(username,end_num)
    region = 'us-west-2'
    
    create_bucket_setup(bucket_name, region)
    
def place_object_in_bucket():
    """
    Places an object in bucket list
    """
    buckets = gen_bucket_list()
    while True:
        try:
            list_all_buckets()
            select_bucket = int(input("Select bucket to insert object: "))
            if select_bucket < count_bucket_list(buckets):
                #print(buckets[select_bucket - 1])
                put_object(buckets[select_bucket - 1])
                break
            else:
                print("Please select from available buckets")
        except:
            print("\nError Occured selecting bucket to place object!")
    
def delete_object_in_bucket():
    """
    Delets an object from bucket list
    """
    buckets = gen_bucket_list()
    while True:
        try:
            list_all_buckets()
            select_bucket = int(input("Select bucket to delete from: "))
            if select_bucket < count_bucket_list(buckets):
                select_name = input("Name of object to delete:")
                delete_object(buckets[select_bucket - 1], select_name)
                break
            else:
                print("Please select from available buckets")
        except:
            print("\nError Occured selecting bucket to delete object!")
    
def delete_bucket():
    """
    Delets a bucket from S3
    """
    buckets = gen_bucket_list()
    while True:
        try:
            list_all_buckets()
            select_bucket = int(input("Select bucket to delete: "))
            if select_bucket < count_bucket_list(buckets):
                delete_bucket_setup(buckets[select_bucket - 1])
                break
            else:
                print("Please select from available buckets")
        except:
            print("\nError Occured selecting bucket to delete!")
    
def copy_from_one_bucket_to_another():
    """
    Copy object to another bucket
    """
    buckets = gen_bucket_list()
    while True:
        try:
            list_all_buckets()
            src_bucket = int(input("Select source bucket: "))
            src_object_name = (input("Select name of object in bucket to move: "))
            dest_bucket = int(input("Select bucket to move object to: "))
            dest_object_name = (input("Select name of copied object: "))
            if src_bucket < count_bucket_list(buckets):
                copy_object(buckets[src_bucket - 1], src_object_name,
                            buckets[dest_bucket - 1], dest_object_name)
                break
            else:
                print("Please select from available buckets")
        except:
            print("\nError Occured copying from one bucket to another!")
    
def download_from_bucket():
    """
    downloads from a bucket
    """
    buckets = gen_bucket_list()
    while True:
        try:
            list_all_buckets()
            select_bucket = int(input("Select bucket to download from: "))
            if select_bucket < count_bucket_list(buckets):
                file = input("Select file to download from {0}: ".format(buckets[select_bucket - 1]))
                new_file_name = input("Select new file name: ")
                download_from_bucket_setup(buckets[select_bucket - 1], file, new_file_name)
                break
            else:
                print("Please select from available buckets")
        except:
            print("\nError Occured selecting bucket to download!")
    
def selected_exit():
    """Exits the program"""
    print("\nProgram Exited:", now)
    print("\n***************************************************************")
    
#****************************************
#        Executes the code
#****************************************
#Main body of the code that calls the last level of functions
while True:#Main
    try:
        selected_choice = int(input("\nWhat S3 funtion would you like "
                                   "to do? "
                                   "\n\t1. Create a bucket"
                                   "\n\t2. Put objects in a previously created bucket"
                                   "\n\t3. Deletes an object in a bucket"
                                   "\n\t4. Deletes a bucket"
                                   "\n\t5. Copy an object from one bucket to another"
                                   "\n\t6. Download an existing object from a bucket"
                                   "\n\t7. Exit the Program\n"))
        if selected_choice == 1:
            create_bucket()
        elif selected_choice == 2:
            place_object_in_bucket()
        elif selected_choice == 3:
            delete_object_in_bucket()
        elif selected_choice == 4:
            delete_bucket()
        elif selected_choice == 5:
            copy_from_one_bucket_to_another()
        elif selected_choice == 6:
            download_from_bucket()
        elif selected_choice == 7:
            selected_exit()
            break
        else:
            print("\nPlease enter 1, 2, 3, 4, 5, 6, or 7")
    except:
        print("\nError Occured in Main!")