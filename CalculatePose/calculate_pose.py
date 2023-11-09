import cv2
import math


class calculate_pose:
#distance between two points
    def distance(self, p1,p2):
        return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

    # compute rotation from {base_angle} to {(x0,y0)->(x1,y1)}
    def calc_relative_angle(x1, y1, x0, y0, base_angle):
        if (y1 == y0) and (x1 == x0):
            return 0
        a1 = np.arctan2(y1 - y0, x1 - x0)
        return pi2pi(a1 - base_angle)

    #finding angle between two keypoints on skeleton using law of cosines
    def find_angle(self, p1,p2):
        calc_d = lambda p1, p0: math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)
        p3 = (p1[0],p2[1])
        a = calc_d(p2,p3) #9-i
        b = calc_d(p1,p3) #8-i
        c = calc_d(p1,p2) #8-9
        return (math.acos((a**2 - b**2 - c**2)/(-2*b*c)))*180/(3.1415926535)

    #finding direction of head relative to camera
    def position(self, human):
        position = "Towards"
        detected = 0
        center_face = [0,14,15,16,17]
        for k in center_face:
            if (k in human):
                detected += 1
        if (detected != 0):
            return position
        else:
            return 'Away'

    #If not enough keypoints, set action to undetermenistic
    def invalid(self, joints):
        if(len(joints[0].keys()) < 6):
            return 'undeterministic'
        else:
            return "false"

    #center of gravity of body using middle openpose skeleton keypoints
    def center_body(self, joints):
        try:
            #neck_x + right_hip_x + left_hip_x
            init_x = float(joints[0][1][0] + joints[0][8][0] + joints[0][11][0]) / 3
            # neck_y + right_hip_y + left_hip_y
            init_y = float(joints[0][1][1] + joints[0][8][1] + joints[0][11][1]) / 3
            # neck_x + right_hip_x + left_hip_x (second frame but same in this case)
            end_x = float(joints[-1][1][0] + joints[-1][8][0] + joints[-1][11][0]) / 3
            # neck_y + right_hip_y + left_hip_y (second frame but same in this case)
            end_y = float(joints[-1][1][1] + joints[-1][8][1] + joints[-1][11][1]) / 3
        except:
            return 'undeterministic'
        return (init_x,init_y,end_x,end_y)

    #center of gravity of body using lower center body openpose skeleton keypoints
    def center_lower_body(self, joints):
        try:
            #(right_hip_y - left_hip_y) / 2 - neck_y
            init_h1 = float(joints[0][8][1] + joints[0][11][1]) / 2 - joints[0][1][1]
            # (right_hip_y - left_hip_y) / 2 - neck_y but same in this case
            end_h1 = float(joints[-1][8][1] + joints[-1][11][1]) / 2 - joints[-1][1][1]
            #((right_knee_y + left_knee_y)  - (right_hip_y - left_hip_y))/2
            init_h2 = (float(joints[0][9][1] + joints[0][12][1]) - float(joints[0][8][1] + joints[0][11][1])) / 2
            ##((right_knee_y + left_knee_y)  - (right_hip_y - left_hip_y))/2 but same in this case
            end_h2 = (float(joints[-1][9][1] + joints[-1][12][1]) - float(joints[-1][8][1] + joints[-1][11][1])) / 2
        except:
            return 'undeterministic'
        return (init_h1,init_h2,end_h1,end_h2)

    #ratio of heights of center_body and center_lower_body
    def point_height_ratio(self, joints):
        center_lower = self.center_lower_body(joints)
        try:
            #ratio of y coordinate height of center_body
            h1 = center_lower[2] / center_lower[0]
        except:
            h1 = 0.0
        try:
            # ratio of y coordinate height of center_lower_body
            h2 = center_lower[3] / center_lower[1]
        except:
            h2 = 0.0
        return (h1,h2)

    #difference of heights of center_body and center_lower_body y coordinates
    def ratio_height_difference(self, joints):
        t = 0.0
        #neck_y
        try:
            ty_1 = float(joints[-1][1][1])
            #(right_hip_y + left_hip_y) /2
            ty_8 = float(joints[-1][8][1] + joints[-1][11][1]) / 2
            ##(right_knee_y + left_knee_y) /2
            ty_9 = float(joints[-1][9][1] + joints[-1][12][1]) / 2

            #ratio of difference of heights in y coordinates of both center bodies
            t = float(ty_8 - ty_1) / (ty_9 - ty_8)
        except:
            t = 0.0
        return t

    #determine action using above ratios/heights of stand,sit,undetermenistic
    def action(self,t,h):
        if  h[0]< 1.16 and h[0] > 0.84 and h[1] < 1.16 and h[1] > 0.84:

            if t < 1.73:
                return 'Stand'
            else:
                return 'Sit'
        else:
            if t < 1.7:
                if h[0] >= 1.08:
                    return 'Stand'
                elif h[0] < 0.92:
                    return 'Stand'
                else:
                    return "Standing"
            else:
                return 'undeterministic'

    #evaluate action of person using above functions
    def move_status(self, joints):
        motion = self.invalid(joints)
        if(motion != 'false'):
            return motion
        t = self.ratio_height_difference(joints)
        h = self.point_height_ratio(joints)
        motion = self.action(t,h)
        return motion

    #draw action and head position relative to camera for each person in image
    def action_text(self, image, all_humans):
        shift = 20
        head_direction = ''
        action = ''
        for human in all_humans:
            head_direction = self.position(human)
            action = self.move_status([human])
            info = head_direction + "," + action
            if 10 in human.keys():
                cv2.putText(image, info ,(30,10 + shift) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            elif 13 in human.keys():
                cv2.putText(image, info, (30, 10 + shift), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            else:
                cv2.putText(image, info, (30, 10 + shift), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 0), 2)
            shift += 20
        return image, head_direction, action
