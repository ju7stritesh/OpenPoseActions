import cv2
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
import logging
from CalculatePose import LyingPose as lying
import os

#testing time purpose
logger = logging.getLogger('TfPoseEstimatorRun')
logger.handlers.clear()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
lying = lying.LyingPose()
body_parts = {'Nose': 0,'Neck' : 1,'RShoulder' : 2, 'RElbow' : 3, 'RWrist' : 4, 'LShoulder' : 5,'LElbow' : 6,'LWrist' : 7,'RHip' : 8,'RKnee' : 9,'RAnkle' : 10,'LHip' : 11,'LKnee' : 12,'LAnkle' : 13,'REye' : 14,'LEye' : 15,'REar' : 16,'LEar' : 17}

#Draws openpose skeleton, action, head position for each person in image
def people_actions():
    w, h = model_wh('432x368')
    e = TfPoseEstimator(get_graph_path('cmu'), target_size=(w, h))
    path = 'Images/'
    for file in os.listdir(path):

        print ("***************Start***************")
        image = cv2.imread(path + file)
        height, width, dim = image.shape
        print (height, width)
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=4.0)
        # image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        all_humans = TfPoseEstimator.draw_humans_joints(image, humans, imgcopy=False)
        for i in range(len(all_humans)):
            upper_body, lower_body, core = lying.body_separation(all_humans[i])
            print(upper_body, lower_body, core)
            angle, distance, image, x, y, theta, ratio = lying.calculate_result(image)
            if 0 <= abs(angle) < 30 and distance < 0.3*height:
                print ("Lying")
                cv2.putText(image, "Lying " + str(int(angle)),(x, y+20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            elif 0 <= abs(angle) < 30 and theta > 35:
                print("Lying")
                cv2.putText(image, "Lying " + str(int(angle)), (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            elif 30 < abs(angle) < 35 and ratio > 0:
                print ("Crouching")
                cv2.putText(image, "Crouching" + str(int(angle)),(x, y+20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            elif 35 <= abs(angle) < 90:
                print ("Sitting")
                cv2.putText(image, "Sitting" + str(int(angle)),(x, y+20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            elif 30 < abs(angle) < 35 and ratio < 0:
                print ("Bending")
                cv2.putText(image, "Bending" + str(int(angle)),(x, y+20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            elif 0 <= abs(angle) < 30 and distance >= 0.3*height:
                print ("Standing")
                cv2.putText(image, "Standing" + str(int(angle)),(x, y+20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            else:
                print ("Undetreministic")
                cv2.putText(image, "UnDeter", (x, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        cv2.imshow("test", image)
        cv2.waitKey(0)
        cv2.imwrite('Results/' + file, image)

if __name__ == '__main__':
    people_actions()
