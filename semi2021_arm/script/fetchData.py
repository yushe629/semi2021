#!/usr/bin/env python
# license removed for brevity
from re import I
import rospy
from rospy.topics import Publisher
from std_msgs.msg import String
from std_msgs.msg import Empty
from std_msgs.msg import UInt8
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from jsk_recognition_msgs.msg import PeoplePoseArray
import math
import time

global baseX
global baseY
baseX = 640/2.0
baseY = 480/2.0

class HumanPoseTeleop:
    def __init__(self):
        self.x = baseX
        self.y = baseY
        self.z = 0.0

        self.human_pose_sub = rospy.Subscriber('/edgetpu_human_pose_estimator/output/poses', PeoplePoseArray, self.callback)
        self.cmd_vel_pub = rospy.Publisher('/tello/cmd_vel', Twist, queue_size=10)
        self.takeoff_pub = rospy.Publisher('/tello/takeoff', Empty, queue_size=1)

    def callback(self, msg):
        right_wrist = (False, 0)
        right_shoulder = (False, 0)
        left_wrist = (False,0)
        left_shoulder = (False,0)

        if msg.poses:
            poses = msg.poses
            limb_names = poses[0].limb_names
            pose = poses[0].poses
            for i,item in enumerate(limb_names):
                if item == 'right wrist':
                    right_wrist = (True,i)
                elif item == 'right shoulder':
                    right_shoulder = (True,i)
                elif item == 'left wrist':
                    left_wrist = (True,i)
                elif item == 'left shoulder':
                    left_shoulder = (True,i)

            right_shoulder_pos = None
            right_wrist_pos = None
            left_shoulder_pos = None
            left_wrist_pos = None

            if right_wrist[0]:
                right_wrist_pos = pose[right_wrist[1]].position
            if left_wrist[0]:
                left_wrist_pos = pose[left_wrist[1]].position
            if right_shoulder[0]:
                right_shoulder_pos = pose[right_shoulder[1]].position
            if left_shoulder[0]:
                left_shoulder_pos = pose[left_shoulder[1]].position

            if right_shoulder_pos is None or left_shoulder_pos is None or \
               right_wrist_pos is None or left_wrist_pos is None:
                return
            
                
            # TODO: implement takeoff / landing
            # if right_wrist_pos.y > right_shoulder_pos.y:
            #     self.takeoff_pub.publish()

            controlX = right_wrist_pos.x - baseX
            controlY = -(right_wrist_pos.y - baseY)

            tw = Twist()
            tw.linear.y = controlX/400.0
            tw.linear.z = controlY/400.0
            if left_wrist_pos.y >= left_shoulder_pos.y:
                tw.linear.y = 0.0
                tw.linear.z = 0.0

            self.cmd_vel_pub.publish(tw)

            str1 = "right: x: {}, y: {} ".format(controlX,controlY)
            str2 = "left: wristY={}, shoulderY={}".format(left_wrist_pos.y, left_shoulder_pos.y)
            rospy.loginfo_throttle(0.5, str1 + str2)

if __name__ == '__main__':
    try:
        rospy.init_node('human_pose_teleop', anonymous=True)
        teleop_node = HumanPoseTeleop()
        rospy.spin()

    except rospy.ROSInterruptException: pass
