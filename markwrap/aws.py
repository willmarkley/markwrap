'''
Python wrapper for the aws command
'''

import os
import re
import botocore
import boto3
import logging
from .util import check


REGION = "us-east-2"

sns = boto3.resource('sns', region_name=REGION)
s3 = boto3.resource('s3', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)

sns_arn_regex = re.compile(r'^arn:aws:sns:us-east-2:\d{12}:\w+$')

def s3_upload(bucket, key, filepath):
	check.nonEmptyString(bucket)
	check.nonEmptyString(key)
	check.fileSizeNonZero(filepath)

	logging.info("Uploading filepath %s to S3 bucket %s with key %s", filepath, bucket, key)
	try:
		s3.Object(bucket, key).upload_file(str(filepath), ExtraArgs={'ServerSideEncryption': 'AES256'})
	except botocore.exceptions.ClientError as e:
		logging.error("Fault from AWS S3 calling upload_file! %s", e)
		logging.error("Fault from AWS S3 calling upload_file! Error: %s", e.response['Error'])
		logging.error("Fault from AWS S3 calling upload_file! ResponseMetadata: %s", e.response['ResponseMetadata'])
		raise e
	except boto3.exceptions.S3UploadFailedError as e:
		logging.error("Fault from AWS S3 calling upload_file! %s", e)
		raise e

	try:
		response = s3_client.list_object_versions(Bucket=bucket, Prefix=key)
	except botocore.exceptions.ClientError as e:
		logging.error("Fault from AWS S3 calling list_object_versions! %s", e)
		logging.error("Fault from AWS S3 calling list_object_versions! Error: %s", e.response['Error'])
		logging.error("Fault from AWS S3 calling list_object_versions! ResponseMetadata: %s", e.response['ResponseMetadata'])
		raise e
	if len(response['Versions']) != 1:
		logging.error("After uploading filepath %s, multiple versions detected in S3 bucket %s for key %s", filepath, bucket, key)
		raise RuntimeError()
	logging.info("Uploaded filepath %s to S3 bucket %s with key %s", filepath, bucket, key)

def s3_download(bucket, key, filepath):
	check.nonEmptyString(bucket)
	check.nonEmptyString(key)
	check.nonexistent(filepath)

	logging.info("Downloading key %s from S3 bucket %s to filepath %s", key, bucket, filepath)
	try:
		s3.Object(bucket, key).download_file(str(filepath))
	except botocore.exceptions.ClientError as e:
		logging.error("Fault from AWS S3 calling download_file! %s", e)
		logging.error("Fault from AWS S3 calling download_file! Error: %s", e.response['Error'])
		logging.error("Fault from AWS S3 calling download_file! ResponseMetadata: %s", e.response['ResponseMetadata'])
		raise e

	logging.info("Downloaded key %s from S3 bucket %s to filepath %s", key, bucket, filepath)

def sns_publish(topic_arn, message):
	check.nonEmptyString(message)
	check.nonEmptyString(topic_arn)
	if not sns_arn_regex.fullmatch(topic_arn):
		logging.error("topic_arn must match the AWS arn format: %s", topic_arn)
		raise RuntimeError()

	logging.info("Publishing message %s to SNS topic %s", message, topic_arn)
	topic = sns.Topic(topic_arn)
	try:
		response = topic.publish(Message=message)
	except botocore.exceptions.ClientError as e:
		logging.error("Fault from AWS SNS calling topic.publish! %s", e)
		logging.error("Fault from AWS SNS calling topic.publish! Error: %s", e.response['Error'])
		logging.error("Fault from AWS SNS calling topic.publish! ResponseMetadata: %s", e.response['ResponseMetadata'])
		raise e
	message_id = response["MessageId"]

	check.nonEmptyString(message_id)
	logging.info("Published message %s to SNS topic %s with messageId %s", message, topic_arn, message_id)
