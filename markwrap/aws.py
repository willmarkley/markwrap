'''
Python wrapper for the aws command
'''

import os
import re
import boto3
import botocore
import logging
from .util import check


REGION = "us-east-2"
aws_client_config = botocore.config.Config(
	region_name = REGION,
	retries = {
		'max_attempts': 3,
		'mode': 'standard'
	}
)


class S3:
	def __init__(self, access_key_id, secret_access_key):
		check.nonEmptyString(access_key_id)
		check.nonEmptyString(secret_access_key)
		self._s3 = boto3.resource('s3', config=aws_client_config, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
		self._s3_client = boto3.client('s3', config=aws_client_config, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

	def upload(self, bucket, key, filepath):
		logging.info("Parameters: bucket=[%s] key=[%s] filepath=[%s]", str(bucket), str(key), str(filepath))
		check.nonEmptyString(bucket)
		check.nonEmptyString(key)
		check.fileSizeNonZero(filepath)

		logging.info("Uploading filepath %s to S3 bucket %s with key %s", filepath, bucket, key)
		try:
			self._s3.Object(bucket, key).upload_file(str(filepath), ExtraArgs={'ServerSideEncryption': 'AES256'})
		except botocore.exceptions.ClientError as e:
			logging.error("Fault from AWS S3 calling upload_file! %s", e)
			logging.error("Fault from AWS S3 calling upload_file! Error: %s", e.response['Error'])
			logging.error("Fault from AWS S3 calling upload_file! ResponseMetadata: %s", e.response['ResponseMetadata'])
			raise e
		except boto3.exceptions.S3UploadFailedError as e:
			logging.error("Fault from AWS S3 calling upload_file! %s", e)
			raise e

		try:
			response = self._s3_client.list_object_versions(Bucket=bucket, Prefix=key)
		except botocore.exceptions.ClientError as e:
			logging.error("Fault from AWS S3 calling list_object_versions! %s", e)
			logging.error("Fault from AWS S3 calling list_object_versions! Error: %s", e.response['Error'])
			logging.error("Fault from AWS S3 calling list_object_versions! ResponseMetadata: %s", e.response['ResponseMetadata'])
			raise e
		if len(response['Versions']) != 1:
			logging.error("After uploading filepath %s, multiple versions detected in S3 bucket %s for key %s", filepath, bucket, key)
			raise RuntimeError()
		logging.info("Uploaded filepath %s to S3 bucket %s with key %s", filepath, bucket, key)

	def download(self, bucket, key, filepath):
		logging.info("Parameters: bucket=[%s] key=[%s] filepath=[%s]", str(bucket), str(key), str(filepath))
		check.nonEmptyString(bucket)
		check.nonEmptyString(key)
		check.nonexistent(filepath)

		logging.info("Downloading key %s from S3 bucket %s to filepath %s", key, bucket, filepath)
		try:
			self._s3.Object(bucket, key).download_file(str(filepath))
		except botocore.exceptions.ClientError as e:
			logging.error("Fault from AWS S3 calling download_file! %s", e)
			logging.error("Fault from AWS S3 calling download_file! Error: %s", e.response['Error'])
			logging.error("Fault from AWS S3 calling download_file! ResponseMetadata: %s", e.response['ResponseMetadata'])
			raise e

		logging.info("Downloaded key %s from S3 bucket %s to filepath %s", key, bucket, filepath)


class SNS:
	_arn_regex = re.compile(r'^arn:aws:sns:us-east-2:\d{12}:\w+$')

	def __init__(self, access_key_id, secret_access_key):
		check.nonEmptyString(access_key_id)
		check.nonEmptyString(secret_access_key)
		self._sns = boto3.resource('sns', config=aws_client_config, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

	def publish(self, topic_arn, message):
		logging.info("Parameters: topic_arn=[%s] message=[%s]", str(topic_arn), str(message))
		check.nonEmptyString(message)
		check.nonEmptyString(topic_arn)
		if not SNS._arn_regex.fullmatch(topic_arn):
			logging.error("topic_arn must match the AWS arn format: %s", topic_arn)
			raise RuntimeError()

		logging.info("Publishing message %s to SNS topic %s", message, topic_arn)
		topic = self._sns.Topic(topic_arn)
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
