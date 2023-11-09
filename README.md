#OpenPose

'OpenPose' is an action pose estimation algorithm implemented using Tensorflow and can return the **actions of a person,skeleton, and head position relative to camera** of all the people in a given image. 

##Prerequisites

-python3
-tensorflow 1.12.0
-tensorflow-base 1.12.0
-tensorflow-gpu 1.12.0
-opencv3, protobuf, python3-tk
-slidingwindow (https://github.com/adamrehn/slidingwindow)
-pycocotools 2.0
-cudatoolkit 9.2
-cudnn 7.2.1
-tqdm
-psutil
-fire
-dill

###Build c++ library for post processing (install swig using pip before doing so)
```
$ cd tf_pose/pafprocess
$ swig -python -c++ pafprocess.i && python3 setup.py build_ext --inplace
```

CMU's model graphs are too large for git, so I uploaded them on an external cloud. You should download them if you want to use cmu's original model. Download scripts are provided in the model folder.

```
$ cd models/graph/cmu
$ bash download.sh
```

###Intall the environment yml file and intialize into the environment before running code


##How to run
	* To run the program:
	* Open up **Action.py**
	* Store the images in **Images**
	* Results will be stored in **Results** (create one if does not exist) folder

##Logic
###This program has the following main functions

- **body_separation**
 	* human is a dictionary of all identifiable keypoints
 	* We separate the body into three parts - upper_body, core, lower_body

- **invalid(joints)**
 	* If joints doesn't have sufficient number of keypoints to make action prediction, it labels action as "undetermenistic

- **calculate_angles**
 	* This calculates the angle between two points

- **calculate_angles_between_two_lines**
 	* Calculates angle between two lines 

- **calculate_result**
 	* This fucntion has the logic to return all neccessary output for action interpretation.
- **people_actions in Action.py**
 	* Given path to an image, it returns a new image with label openpose skeletons, action, head_direction for each person in image
  		* **TfPoseEstimator.draw_humans** draws openpose skeleton for each person in image
  		* **TfPoseEstimator.draw_humans_joints** returns list of dictionaries of keypoints for each person in image
  		* Run **LyingPose** on image to receive final image with all info 

##Extra

###Logic
Law of cosines were used to analyze varying degree angles from keypoints. The ratios of the lower body coordinates
and especially the y coordinates were used along with distances between coordinates to make a final prediction on action.

###Keypoint info
	-Nose = 0
	-Neck = 1
	-RShoulder = 2
	-RElbow = 3
	-RWrist = 4
	-LShoulder = 5
	-LElbow = 6
	-LWrist = 7
	-RHip = 8
	-RKnee = 9
	-RAnkle = 10
	-LHip = 11
	-LKnee = 12
	-LAnkle = 13
	-REye = 14
	-LEye = 15
	-REar = 16
	-LEar = 17

author - ju7stritesh@gmail.com