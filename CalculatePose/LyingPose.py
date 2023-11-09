import math
import cv2

class LyingPose():
    def __init__(self):

        self.upper_body = {}
        self.lower_body = {}
        self.core = {}
        self.knee = {}

    def body_separation(self, all_humans):

        self.upper_body = {}
        self.lower_body = {}
        self.core = {}
        for key in all_humans:
            if key == 0:
                self.upper_body['Nose'] = all_humans[key]
            if key == 1:
                self.upper_body['Neck'] = all_humans[key]
            if key == 2:
                self.upper_body['Rshoulder'] = all_humans[key]
            if key == 5:
                self.upper_body['Lshoulder'] = all_humans[key]
            if key == 14 or key == 15:
                self.upper_body['eye'] = all_humans[key]
            if key == 16 or key == 17:
                self.upper_body['ear'] = all_humans[key]

            if key == 11:
                self.core['Lhip'] = all_humans[key]
            if key == 8:
                self.core['Rhip'] = all_humans[key]

            if key == 9:
                self.lower_body['Rknee'] = all_humans[key]
            if key == 10:
                self.lower_body['Rankle'] = all_humans[key]
            if key == 12:
                self.lower_body['Lknee'] = all_humans[key]
                self.knee['Rknee'] = all_humans[key]
            if key == 13:
                self.lower_body['Lankle'] = all_humans[key]
                self.knee['Lknee'] = all_humans[key]

        return self.upper_body, self.lower_body, self.core

    def calculate_angles(self, x1,y1,x2,y2):
        if x2 == x1:
            diff = -1
        else:
            diff = x2-x1
        slope = (y2 - y1) / diff
        theta = math.degrees(math.atan(slope))
        dist = abs(y2 - y1)
        return slope, theta, dist

    def calculate_angles_two_lines(self, m1, m2):
        diff = m1 - m2
        tantheta = diff/(1+m1*m2)
        angle = math.degrees(math.atan(tantheta))
        return angle

    def calculate_result(self, image):
        angle = -1000
        dist3 = 0
        theta3 = 0
        ratio = 0
        x1=y1=x2=y2=x3=y3=0
        if len(self.lower_body) > 0:
            if 'Rknee' in self.lower_body:
                x1,y1 = self.lower_body['Rknee']
            elif 'Lknee' in self.lower_body:
                x1,y1 = self.lower_body['Lknee']

        if len(self.upper_body) > 0:
            if 'Nose' in self.upper_body:
                x2,y2 = self.upper_body['Nose']
            elif 'Neck' in self.upper_body:
                x2,y2 = self.upper_body['Neck']
            elif 'eye' in self.upper_body:
                x2,y2 = self.upper_body['eye']
            elif 'ear' in self.upper_body:
                x2,y2 = self.upper_body['ear']

        if len(self.core) > 0:
            if 'Rhip' in self.core:
                x3,y3 = self.core['Rhip']
            else:
                x3,y3 = self.core['Lhip']

        if x1 > 0 and x3 > 0 and x2 > 0:

            slope1, theta1, dist1 = self.calculate_angles(x1,y1,x3,y3)
            slope2, theta2, dist2 = self.calculate_angles(x2,y2,x3,y3)
            angle = self.calculate_angles_two_lines(slope1, slope2)
            if (y3-y1) != 0:
                ratio = (y3-y2)/(y3-y1)

            print('Angle between lines', angle, theta1, theta2, ratio)

        if x1 > 0 and x2 > 0:
            slope3, theta3, dist3 = self.calculate_angles(x1,y1,x2,y2)

            image = cv2.line(image, (x1, y1), (x3, y3), (255, 255, 255), 2)

            image = cv2.line(image, (x2, y2), (x3, y3), (255, 255, 255), 2)
            if theta3 < 0:
                theta3 = 90 + theta3
            else:
                theta3 = 90 - theta3

            print ('Distance',dist3, theta3)

        return angle, dist3, image, x2, y2, theta3, ratio
