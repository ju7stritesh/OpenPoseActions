import os
import sys
import io
from PIL import Image
import numpy as np

# pipeline = os.getenv('pipeline', "Develop")

sys.path.append("src")
sys.path.append("utils")
sys.path.append("confidence_face")

import boto3
import json
from botocore.config import Config as BotoCoreConfig
from sentrycommon import PipelineConfig as conf
import Constants as con
import StatusCode as sc
import image_pose
import time
from sentrycommon import Logger
import logging
from sentrycommon import SentryAWSClients as AwsClient

start_time = time.time()
print('Loading finished: ' + str(time.time() - start_time))


class Worker:
    def __init__(self):

        LogSetup = Logger.Logger_Setup()
        self.logger = logging.getLogger(__name__)
        LogSetup.set_level(self.logger)

        boto_config = BotoCoreConfig(read_timeout=70, region_name=conf.REGION)

        self.step_client = boto3.client('stepfunctions', aws_access_key_id=conf.AWS_ACCESS_KEY,
                                        aws_secret_access_key=conf.AWS_SECRET_KEY, config=boto_config)
        self.activity_arn = con.ARN_URL
        self.pose = image_pose.image_pose()

    def image_bytes_to_pil_image(self, image_bytes):
        return Image.open(io.BytesIO(image_bytes))

    def listen(self):
        activity_time = 0
        while True:
            self.logger.debug('Activity peocessing time: ' + str(time.time() - activity_time))
            start_time = time.time()

            activity = self.step_client.get_activity_task(activityArn=self.activity_arn)
            activity_time = time.time()
            self.logger.debug('****************************   Activity received at: ' + str(time.time()))
            self.logger.debug('Received an activity. Processing it, ' + str(time.time() - start_time))
            task_token = activity.get('taskToken', None)

            if task_token:

                input = activity.get("input")
                meta_data = json.loads(input)
                image_id = meta_data['image_id']
                if len(image_id) == 1:
                    image_id = image_id[0]
                    self.logger.debug('Get adn load activity cumulative: ' + str(time.time() - activity_time))
                    print (image_id)
                    try:
                        image_bytes = AwsClient.SentryS3().get_from_s3('posebucket', image_id)
                        # print (image_bytes)
                        pil_image = self.image_bytes_to_pil_image(image_bytes)
                        image = np.array(pil_image)
                        keypoints = self.pose.people_actions(image)
                        # print (keypoints)

                        if len(keypoints) > 0:
                            print (keypoints)

                        else:
                            status_codes = []
                            error_code = 415
                            response_message = []
                            status_codes.append(error_code)
                            response_message.append(sc.STATUS_CODE[error_code])


                        json_output = keypoints
                        print (json_output)
                        self.step_client.send_task_success(taskToken=task_token, output=json.dumps(
                            json_output))  # This is not received by the API caller (?)
                        self.logger.debug('Send task cumulative: ' + str(time.time() - activity_time))
                    except Exception as ex:
                        print ("Exception : ", ex)
                else:
                    print("Feature not Integrated yet")
                    json_output = '{"Message":"Feature not Integrated yet"}'
                    json_output = json.loads(json_output)
                    self.step_client.send_task_success(taskToken=task_token, output=json.dumps(
                        json_output))  # This is not received by the API caller (?)
                    self.logger.debug('Send task cumulative: ' + str(time.time() - activity_time))


            else:
                status_code = 202
                print(sc.STATUS_CODE[status_code])
                print('No image received')


print('Start')
worker = Worker()
worker.listen()
