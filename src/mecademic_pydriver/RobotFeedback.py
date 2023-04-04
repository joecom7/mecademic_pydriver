import socket

from mecademic_pydriver.MessageReceiver import MessageReceiver
from mecademic_pydriver.parsingLib import extract_payload_from_messages, payload2tuple, status_robot_list2dict


class RobotFeedback:
    """Class for the Mecademic Robot allowing for live positional 
    feedback of the Mecademic Robot 

    Joint Angles, angles in degrees | [theta_1, theta_2, ... theta_n]
    Cartesian coordinates, distances in mm, angles in degrees | [x,y,z,alpha,beta,gamma]

    Attributes:
        Address: IP Address
        socket: socket connecting to physical Mecademic Robot
    """

    def __init__(self, address, socket_timeout=0.1, firmware_version_9=True, firmware_version_8=False):
        """Constructor for an instance of the Class Mecademic Robot 

        :param address: The IP address associated to the Mecademic Robot
        """
        self.address = address
        self.port = 10001

        self.socket = None
        self.socket_timeout = socket_timeout

        self.message_receiver = None
        self.message_terminator = "\x00"

        self.firmware_version_9 = firmware_version_9

        if self.firmware_version_9:
            # v9.2.2
            print("RobotFeedback: Selected Version 9")
            self.rt_joints_fb_code = "2210"
            self.rt_pose_fb_code = "2201"
            self.rt_cart_vel_code = "2214"
            self.status_robot_fb_code = "2007"
        elif firmware_version_8:
            # 8.0.8.1-beta
            print("RobotFeedback: Selected Version 8 - Beta")
            self.joints_fb_code = "2026"
            self.pose_fb_code = "2027"
            self.status_robot_fb_code = "2007"
        else:
            # 7.0.6
            self.joints_fb_code = "2102"
            self.pose_fb_code = "2103"
            self.status_robot_fb_code = "2007"  # never received in version 7

    def connect(self):
        """Connects Mecademic Robot object communication to the physical Mecademic Robot

        May raise an Exception
        """
        # create a socket and connect
        self.socket = socket.socket()
        self.socket.settimeout(self.socket_timeout)
        self.socket.connect((self.address, self.port))
        self.socket.settimeout(self.socket_timeout)

        # check that socket is not connected to nothing
        if self.socket is None:
            raise RuntimeError("RobotFeedback::Connect - socket is None")

        self.message_receiver = MessageReceiver(
            self.socket, self.message_terminator)

    def disconnect(self):
        """Disconnects Mecademic Robot object from physical Mecademic Robot
        """
        if(self.socket is not None):
            self.socket.close()
            self.socket = None

    def get_data(self, wait_for_new_messages=True, timeout=None):
        """
        Receives message from the Mecademic Robot and 
        saves the values in appropriate variables
        return (joints,pose,status_robot)
        wait_for_new_messages : bool (Default True)
            if wait for new messages
        """
        if self.socket is None:  # check that the connection is established
            # if no connection, nothing to receive
            raise RuntimeError("RobotFeedback::getData - socket is None")

        # read message from robot
        if wait_for_new_messages:
            self.message_receiver.wait_for_new_messages(timeout)
        messages = self.message_receiver.get_last_messages(10)

        joints = None
        pose = None
        robot_status = None
        cart_vel = None
        if messages:
            messages.reverse()  # reverse the messages to get the newer
            if self.firmware_version_9:
                joints = self.set_rt_joints_from_messages(messages)
                pose = self.set_rt_pose_from_messages(messages)
                cart_vel = self.set_rt_cart_vel_from_messages(messages)
            else:
                joints = self.set_joints_from_messages(messages)
                pose = self.set_pose_from_messages(messages)
            
            robot_status = self.set_status_robot_from_messages(messages)

        return joints, pose, cart_vel, robot_status

    def set_joints_from_messages(self, messages):
        """
        set joints from message list
        set the joints using the first occurance in messages
        """
        joints_payload = extract_payload_from_messages(
            self.joints_fb_code,
            messages
        )
        if joints_payload:
            return payload2tuple(joints_payload)
        else:
            return None

    def set_rt_joints_from_messages(self, messages):
        """
        set joints from message list RT
        set the joints using the first occurance in messages
        """
        joints_payload = extract_payload_from_messages(
            self.rt_joints_fb_code,
            messages
        )
        if joints_payload:
            return payload2tuple(joints_payload)
        else:
            return None

    def set_pose_from_messages(self, messages):
        """
        set pose from message list
        set the pose using the first occurance in messages
        """
        pose_payload = extract_payload_from_messages(
            self.pose_fb_code,
            messages
        )
        if pose_payload:
            return payload2tuple(pose_payload)
        return None

    def set_rt_pose_from_messages(self, messages):
        """
        set pose from message list RT
        set the pose using the first occurance in messages
        """
        pose_payload = extract_payload_from_messages(
            self.rt_pose_fb_code,
            messages
        )
        if pose_payload:
            return payload2tuple(pose_payload)
        return None

    def set_rt_cart_vel_from_messages(self, messages):
        """
        NOTE: t, x_dot, y_dot , z_dot , wx, wy, wz
        set rt cart vel from message list: TRF with respect to the WRF
        set the rt cartesian velocity using the first occurance in messages
        """
        pose_payload = extract_payload_from_messages(
            self.rt_cart_vel_code,
            messages
        )
        if pose_payload:
            return payload2tuple(pose_payload)
        return None

    def set_status_robot_from_messages(self, messages):
        """
        set status robot from message list
        set the status robot using the first occurance in messages
        """
        pass
        status_robot_payload = extract_payload_from_messages(
            self.status_robot_fb_code,
            messages
        )
        if status_robot_payload:
            return status_robot_list2dict(payload2tuple(status_robot_payload))
        else:
            return None
