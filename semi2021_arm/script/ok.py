#!/usr/bin/env python
# license removed for brevity
from re import I
from rosgraph.xmlrpc import SilenceableXMLRPCRequestHandler
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

# useRightHand
global width
global height
width = 640
height = 480

global baseX
global baseY
global halfX
halfX = width/2.0
baseX = width/4.0
baseY = height/2.0

class HumanPoseTeleop:
    def __init__(self):

        self.human_pose_sub = rospy.Subscriber('/edgetpu_human_pose_estimator/output/poses', PeoplePoseArray, self.callback)
        self.chat_pub = rospy.Publisher('chatter', String, queue_size=10);
        time.sleep(1.0)
        rospy.Publisher('tello/takeoff',Empty,queue_size=1).publish()

    def setZero(self, twist):
        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0

    def callback(self, msg):
        right_wrist = (False, 0)
        right_shoulder = (False, 0)
        right_elbow = (False, 0)
        left_wrist = (False,0)
        left_shoulder = (False,0)
        left_elbow = (False, 0)
        nose = (False, 0)

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
                elif item == 'right elbow':
                    right_elbow = (True,i)
                elif item == 'left elbow':
                    left_elbow = (True,i)
                elif item == 'nose':
                    nose = (True,i)

            right_shoulder_pos = None
            right_wrist_pos = None
            left_shoulder_pos = None
            left_wrist_pos = None
            nose_pos = None
            left_elbow_pos = None
            right_elbow_pos = None

            if right_wrist[0]:
                right_wrist_pos = pose[right_wrist[1]].position
            if left_wrist[0]:
                left_wrist_pos = pose[left_wrist[1]].position
            if right_shoulder[0]:
                right_shoulder_pos = pose[right_shoulder[1]].position
            if left_shoulder[0]:
                left_shoulder_pos = pose[left_shoulder[1]].position
            if nose[0]:
                nose_pos = pose[nose[1]].position
            if right_elbow[0]:
                right_elbow_pos = pose[right_elbow[1]].position
            if left_elbow[0]:
                left_elbow_pos = pose[left_elbow[1]].position
            
            if left_elbow_pos.x > left_wrist_pos.x and right_elbow_pos.x < right_wrist_pos.x:
                if left_wrist_pos.y < left_elbow_pos.y and right_wrist_pos.y < right_elbow_pos.y:
                    str = 'OK'
                    rospy.loginfo_throttle(0.5,str)
                elif left_wrist_pos.y > left_elbow_pos.y and right_wrist_pos.y > right_elbow_pos.y:
                    str = 'naka'
                    rospy.loginfo_throttle(0.5, str)

            time.sleep(1.0)

if __name__ == '__main__':
    try:
        rospy.init_node('human_pose_teleop', anonymous=True)
        teleop_node = HumanPoseTeleop()
        rospy.spin()

    except rospy.ROSInterruptException: pass
