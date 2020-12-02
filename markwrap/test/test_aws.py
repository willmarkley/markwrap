import markwrap.aws as aws
import json
import os
import logging
import botocore
import boto3
import filecmp
from moto import mock_sns
from moto import mock_sqs
from moto import mock_s3
import pytest
import shutil
import markwrap.test.constants as tstconst

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'

@mock_s3
def test_upload(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_BUCKET = "test.bucket"
	HAPPY_PATH_KEY = "test/object"
	HAPPY_PATH_FILEPATH = TMP_DIR / tstconst.EXISTING_FILE
	HAPPY_PATH_VERIFICATION_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE

	ERROR_RELATIVE_FILEPATH = tstconst.EXISTING_FILE
	ERROR_NON_EXISTENT_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE
	ERROR_EMPTY_FILE = TMP_DIR / tstconst.EMPTY_FILE
	ERROR_NON_EXISTENT_BUCKET = "does.not.exist"

	s3 = aws.S3('testing', 'testing')
	caplog.clear()

## INVALID INPUT
	with pytest.raises(RuntimeError):
		s3.upload(None, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)
	assert caplog.text == "[ERROR] check.nonNone - can NOT be None: None\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.upload("", HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)
	assert caplog.text == "[ERROR] check.nonEmptyString - string cannot be empty: \n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.upload(HAPPY_PATH_BUCKET, None, HAPPY_PATH_FILEPATH)
	assert caplog.text == "[ERROR] check.nonNone - can NOT be None: None\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.upload(HAPPY_PATH_BUCKET, "", HAPPY_PATH_FILEPATH)
	assert caplog.text == "[ERROR] check.nonEmptyString - string cannot be empty: \n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.upload(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, ERROR_RELATIVE_FILEPATH)
	assert caplog.text == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_FILEPATH) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.upload(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, ERROR_NON_EXISTENT_FILE)
	assert caplog.text == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NON_EXISTENT_FILE) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.upload(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, ERROR_EMPTY_FILE)
	assert caplog.text == "[ERROR] check.fileSizeNonZero - file size is not greater than zero: " + str(ERROR_EMPTY_FILE) + " (0 bytes)\n"
	caplog.clear()

## MOCK AWS SETUP
	caplog.set_level(logging.INFO)
	moto_s3 = boto3.resource('s3', region_name=aws.REGION)
	test_bucket = moto_s3.create_bucket(Bucket=HAPPY_PATH_BUCKET, CreateBucketConfiguration={'LocationConstraint': aws.REGION})
	test_bucket_versioning = test_bucket.Versioning()
	test_bucket_versioning.enable()
	moto_s3_client = boto3.client('s3', region_name=aws.REGION)
	moto_s3_client.put_bucket_encryption(Bucket=HAPPY_PATH_BUCKET, ServerSideEncryptionConfiguration={'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]})
	moto_s3_client.put_bucket_lifecycle_configuration(Bucket=HAPPY_PATH_BUCKET, LifecycleConfiguration={
        'Rules': [
            {
                'Expiration': {
                    'Days': 3650,
                },
                'Filter': {
                    'Prefix': '',
                },
                'ID': 'TestOnly',
                'Status': 'Enabled'
            }
		]
	})
	caplog.clear()

## HAPPY PATH
	s3.upload(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)

	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] aws.upload - Uploading filepath " + str(HAPPY_PATH_FILEPATH) + " to S3 bucket " + HAPPY_PATH_BUCKET + " with key " + HAPPY_PATH_KEY
	assert lines[1] == "[INFO] aws.upload - Uploaded filepath " + str(HAPPY_PATH_FILEPATH) + " to S3 bucket " + HAPPY_PATH_BUCKET + " with key " + HAPPY_PATH_KEY
	caplog.clear()
	test_bucket.download_file(HAPPY_PATH_KEY, str(HAPPY_PATH_VERIFICATION_FILE))
	filecmp.cmp(HAPPY_PATH_FILEPATH, HAPPY_PATH_VERIFICATION_FILE, shallow=False)
	os.remove(HAPPY_PATH_VERIFICATION_FILE)

## OVERWRITE FAILURE
	with pytest.raises(RuntimeError):
		s3.upload(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] aws.upload - Uploading filepath " + str(HAPPY_PATH_FILEPATH) + " to S3 bucket " + HAPPY_PATH_BUCKET + " with key " + HAPPY_PATH_KEY
	assert lines[1] == "[ERROR] aws.upload - After uploading filepath " + str(HAPPY_PATH_FILEPATH) + ", multiple versions detected in S3 bucket " + HAPPY_PATH_BUCKET + " for key " + HAPPY_PATH_KEY
	caplog.clear()

## DEPENDENCY FAILURE
	with pytest.raises(boto3.exceptions.S3UploadFailedError):
		s3.upload(ERROR_NON_EXISTENT_BUCKET, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] aws.upload - Uploading filepath " + str(HAPPY_PATH_FILEPATH) + " to S3 bucket " + ERROR_NON_EXISTENT_BUCKET + " with key " + HAPPY_PATH_KEY
	assert lines[1] == "[ERROR] aws.upload - Fault from AWS S3 calling upload_file! Failed to upload " + str(HAPPY_PATH_FILEPATH) + " to " + ERROR_NON_EXISTENT_BUCKET + "/" + HAPPY_PATH_KEY + ": An error occurred (NoSuchBucket) when calling the PutObject operation: The specified bucket does not exist"
	caplog.clear()

@mock_s3
def test_download(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_BUCKET = "test.bucket"
	HAPPY_PATH_KEY = "test/object"
	HAPPY_PATH_FILEPATH = TMP_DIR / tstconst.NONEXISTENT_FILE
	HAPPY_PATH_OUTPUT_CONTENT = TMP_DIR / tstconst.EXISTING_FILE

	ERROR_RELATIVE_FILEPATH = tstconst.EXISTING_FILE
	ERROR_EXISTING_FILE = TMP_DIR / tstconst.EXISTING_FILE
	ERROR_NON_EXISTENT_BUCKET = "does.not.exist"
	ERROR_NON_EXISTENT_KEY = "does/not/exist"

	s3 = aws.S3('testing', 'testing')
	caplog.clear()

## INVALID INPUT
	with pytest.raises(RuntimeError):
		s3.download(None, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)
	assert caplog.text == "[ERROR] check.nonNone - can NOT be None: None\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.download(HAPPY_PATH_BUCKET, None, HAPPY_PATH_FILEPATH)
	assert caplog.text == "[ERROR] check.nonNone - can NOT be None: None\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.download(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, ERROR_RELATIVE_FILEPATH)
	assert caplog.text == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_FILEPATH) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		s3.download(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, ERROR_EXISTING_FILE)
	assert caplog.text == "[ERROR] check.nonexistent - file or directory already exists: " + str(ERROR_EXISTING_FILE) + "\n"
	caplog.clear()

## MOCK AWS SETUP
	caplog.set_level(logging.INFO)
	moto_s3 = boto3.resource('s3', region_name=aws.REGION)
	test_bucket = moto_s3.create_bucket(Bucket=HAPPY_PATH_BUCKET, CreateBucketConfiguration={'LocationConstraint': aws.REGION})
	test_bucket_versioning = test_bucket.Versioning()
	test_bucket_versioning.enable()
	moto_s3_client = boto3.client('s3', region_name=aws.REGION)
	moto_s3_client.put_bucket_encryption(Bucket=HAPPY_PATH_BUCKET, ServerSideEncryptionConfiguration={'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]})
	moto_s3_client.put_bucket_lifecycle_configuration(Bucket=HAPPY_PATH_BUCKET, LifecycleConfiguration={
        'Rules': [
            {
                'Expiration': {
                    'Days': 3650,
                },
                'Filter': {
                    'Prefix': '',
                },
                'ID': 'TestOnly',
                'Status': 'Enabled'
            }
		]
	})
	caplog.clear()

## HAPPY PATH
	test_bucket.upload_file(str(HAPPY_PATH_OUTPUT_CONTENT), HAPPY_PATH_KEY)

	s3.download(HAPPY_PATH_BUCKET, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)

	filecmp.cmp(HAPPY_PATH_FILEPATH, HAPPY_PATH_OUTPUT_CONTENT, shallow=False)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] aws.download - Downloading key " + HAPPY_PATH_KEY + " from S3 bucket " + HAPPY_PATH_BUCKET + " to filepath " + str(HAPPY_PATH_FILEPATH)
	assert lines[1] == "[INFO] aws.download - Downloaded key " + HAPPY_PATH_KEY + " from S3 bucket " + HAPPY_PATH_BUCKET + " to filepath " + str(HAPPY_PATH_FILEPATH)
	caplog.clear()
	os.remove(HAPPY_PATH_FILEPATH)

## DEPENDENCY FAILURE
	with pytest.raises(botocore.exceptions.ClientError):
		s3.download(ERROR_NON_EXISTENT_BUCKET, HAPPY_PATH_KEY, HAPPY_PATH_FILEPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 4
	assert lines[0] == "[INFO] aws.download - Downloading key " + HAPPY_PATH_KEY + " from S3 bucket " + ERROR_NON_EXISTENT_BUCKET + " to filepath " + str(HAPPY_PATH_FILEPATH)
	assert lines[1] == "[ERROR] aws.download - Fault from AWS S3 calling download_file! An error occurred (NoSuchBucket) when calling the HeadObject operation: The specified bucket does not exist"
	assert lines[2].startswith("[ERROR] aws.download - Fault from AWS S3 calling download_file! Error: {'Code': 'NoSuchBucket', 'Message': 'The specified bucket does not exist', 'BucketName': 'does.not.exist', 'RequestID': ")
	assert lines[3] == "[ERROR] aws.download - Fault from AWS S3 calling download_file! ResponseMetadata: {'HTTPStatusCode': 404, 'HTTPHeaders': {}, 'RetryAttempts': 0}"
	caplog.clear()

	with pytest.raises(botocore.exceptions.ClientError):
		s3.download(HAPPY_PATH_BUCKET, ERROR_NON_EXISTENT_KEY, HAPPY_PATH_FILEPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 4
	assert lines[0] == "[INFO] aws.download - Downloading key " + ERROR_NON_EXISTENT_KEY + " from S3 bucket " + HAPPY_PATH_BUCKET + " to filepath " + str(HAPPY_PATH_FILEPATH)
	assert lines[1] == "[ERROR] aws.download - Fault from AWS S3 calling download_file! An error occurred (404) when calling the HeadObject operation: Not Found"
	assert lines[2] == "[ERROR] aws.download - Fault from AWS S3 calling download_file! Error: {'Code': '404', 'Message': 'Not Found'}"
	assert lines[3] == "[ERROR] aws.download - Fault from AWS S3 calling download_file! ResponseMetadata: {'RequestId': '', 'HostId': '', 'HTTPStatusCode': 404, 'HTTPHeaders': {}, 'RetryAttempts': 0}"
	caplog.clear()


@mock_sns
@mock_sqs
def test_sns_publish(caplog):
	caplog.set_level(logging.DEBUG)

	HAPPY_PATH_TOPIC_NAME = "TestTopic"
	HAPPY_PATH_TOPIC_ARN = "arn:aws:sns:us-east-2:123456789012:" + HAPPY_PATH_TOPIC_NAME
	HAPPY_PATH_MESSAGE = "Test Message"

	ERROR_BAD_TOPIC_ARN = "arn:aws::us-east-2:123456789012:TestTopic"
	ERROR_NON_EXISTENT_TOPIC_ARN = "arn:aws:sns:us-east-2:123456789012:DoesNotExist"

	sns = aws.SNS('testing', 'testing')
	caplog.clear()

## INVALID INPUT
	with pytest.raises(RuntimeError):
		sns.publish(None, HAPPY_PATH_MESSAGE)
	assert caplog.text == "[ERROR] check.nonNone - can NOT be None: None\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		sns.publish(HAPPY_PATH_TOPIC_ARN, None)
	assert caplog.text == "[ERROR] check.nonNone - can NOT be None: None\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		sns.publish(ERROR_BAD_TOPIC_ARN, HAPPY_PATH_MESSAGE)
	assert caplog.text == "[ERROR] aws.publish - topic_arn must match the AWS arn format: " + str(ERROR_BAD_TOPIC_ARN) + "\n"
	caplog.clear()

## MOCK AWS SETUP
	caplog.set_level(logging.INFO)
	moto_sns = boto3.resource('sns', region_name=aws.REGION)
	test_topic = moto_sns.create_topic(Name=HAPPY_PATH_TOPIC_NAME)

	moto_sqs = boto3.client('sqs', region_name=aws.REGION)
	test_queue_url = moto_sqs.create_queue(QueueName="test_queue")["QueueUrl"]
	test_queue_arn = moto_sqs.get_queue_attributes(QueueUrl=test_queue_url, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]

	test_topic.subscribe(Protocol='sqs', Endpoint=test_queue_arn)
	caplog.clear()

## HAPPY PATH
	sns.publish(HAPPY_PATH_TOPIC_ARN, HAPPY_PATH_MESSAGE)

	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] aws.publish - Publishing message " + str(HAPPY_PATH_MESSAGE) + " to SNS topic " + str(HAPPY_PATH_TOPIC_ARN)
	assert lines[1].startswith("[INFO] aws.publish - Published message " + str(HAPPY_PATH_MESSAGE) + " to SNS topic " + str(HAPPY_PATH_TOPIC_ARN) + " with messageId ")
	caplog.clear()
	messages = moto_sqs.receive_message(QueueUrl=test_queue_url)["Messages"]
	assert len(messages) == 1
	sns_notification = json.loads(messages[0]["Body"])
	assert HAPPY_PATH_TOPIC_ARN == sns_notification["TopicArn"]
	assert HAPPY_PATH_MESSAGE == sns_notification["Message"]

## DEPENDENCY FAILURE
	with pytest.raises(botocore.exceptions.ClientError):
		sns.publish(ERROR_NON_EXISTENT_TOPIC_ARN, HAPPY_PATH_MESSAGE)
	lines = caplog.text.splitlines()
	assert len(lines) == 4
	assert lines[0] == "[INFO] aws.publish - Publishing message " + str(HAPPY_PATH_MESSAGE) + " to SNS topic " + str(ERROR_NON_EXISTENT_TOPIC_ARN)
	assert lines[1] == "[ERROR] aws.publish - Fault from AWS SNS calling topic.publish! An error occurred (NotFound) when calling the Publish operation: Endpoint with arn arn:aws:sns:us-east-2:123456789012:DoesNotExist not found"
	assert lines[2] == "[ERROR] aws.publish - Fault from AWS SNS calling topic.publish! Error: {'Code': 'NotFound', 'Message': 'Endpoint with arn arn:aws:sns:us-east-2:123456789012:DoesNotExist not found'}"
	assert lines[3] == "[ERROR] aws.publish - Fault from AWS SNS calling topic.publish! ResponseMetadata: {'HTTPStatusCode': 404, 'HTTPHeaders': {'server': 'amazon.com', 'status': '404'}, 'RetryAttempts': 0}"
	caplog.clear()
