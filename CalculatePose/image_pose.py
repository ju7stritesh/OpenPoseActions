import math
import cv2
from tf_pose import common
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
import logging
import numpy as np
import time
from calculate_pose import calculate_pose

class image_pose:
    def __init__(self):
        self.inference, self.width, self.height = self.initiaize_model()
        self.calculate_pose = calculate_pose()

    def initiaize_model(self):
        w, h = model_wh('432x368')
        e = TfPoseEstimator(get_graph_path('cmu'), target_size=(w, h))
        return e,w,h

    #Draws openpose skeleton, action, head position for each person in image
    def people_actions(self, image):
        # image = common.read_imgfile(imagepath, None, None)
        start_time = time.time()
        humans = self.inference.inference(image, resize_to_default=(self.width > 0 and self.height > 0), upsample_size=4.0)
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        all_humans = TfPoseEstimator.draw_humans_joints(image, humans, imgcopy=False)
        # image, head_direction, action = self.calculate_pose.action_text(image,all_humans)
        print (time.time() - start_time)

        # cv2.imshow("img", image)
        # cv2.waitKey(10)
        return all_humans

if __name__ == '__main__':
    pose = image_pose()
    image = cv2.imread('images/apink3.jpg')
    pose.people_actions(image)
