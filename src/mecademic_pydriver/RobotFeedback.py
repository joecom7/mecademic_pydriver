import socket

from .messageReceiver import messageReceiver
from .parsingLib import extract_payload_from_messages, payload2tuple

class RobotFeedback:
    """Class for the Mecademic Robot allowing for live positional 
    feedback of the Mecademic Robot 

    Attributes:
        Address: IP Address
        socket: socket connecting to physical Mecademic Robot
        joints: tuple of the joint angles in degrees
        pose: tuple of the cartesian values in mm and degrees
    """

    def __init__(self, address, socket_timeout=0.1):
        """Constructor for an instance of the Class Mecademic Robot 

        :param address: The IP address associated to the Mecademic Robot
        """
        self.address = address
        self.port = 10001

        self.socket = None
        self.socket_timeout = socket_timeout
        
        self.message_receiver = None
        self.message_terminator = "\x00"

        self.joints_fb_code = "2102"
        self.pose_fb_code = "2103"

        self.joints = ()    #Joint Angles, angles in degrees | [theta_1, theta_2, ... theta_n]
        self.pose = () #Cartesian coordinates, distances in mm, angles in degrees | [x,y,z,alpha,beta,gamma]

    def connect(self):
        """Connects Mecademic Robot object communication to the physical Mecademic Robot

        May raise an Exception
        """
        #create a socket and connect
        self.socket = socket.socket()
        self.socket.settimeout(self.socket_timeout)
        self.socket.connect((self.address, self.port))
        self.socket.settimeout(self.socket_timeout)

        #check that socket is not connected to nothing
        if self.socket is None:          
            raise RuntimeError( "RobotFeedback::Connect - socket is None" )

        self.message_receiver = messageReceiver(self.socket, self.message_terminator)
    
    def disconnect(self):
        """Disconnects Mecademic Robot object from physical Mecademic Robot
        """
        if(self.socket is not None):
            self.socket.close()
            self.socket = None        

    def get_data(self, wait_for_new_messages=True):
        """
        Receives message from the Mecademic Robot and 
        saves the values in appropriate variables
        return (joints, pose)
        wait_for_new_messages : bool (Default True)
            if wait for new messages
        """
        if self.socket is None: #check that the connection is established
            raise RuntimeError( "RobotFeedback::getData - socket is None" ) #if no connection, nothing to receive
        
        #read message from robot
        self.message_receiver.wait_for_new_messages()
        messages = self.message_receiver.get_last_messages(10)
        messages.reverse() #reverse the messages to get the newer

        if messages:
            self.set_joints_from_messages(messages)
            self.set_pose_from_messages(messages)

        return self.joints, self.pose

    def set_joints_from_messages(self, messages):
        """
        set joints from message list
        set the joints using the first occurance in messages
        """
        self.joints = payload2tuple(
            extract_payload_from_messages(
                self.joints_fb_code, 
                messages
            )
        )

    def set_pose_from_messages(self, messages):
        """
        set pose from message list
        set the pose using the first occurance in messages
        """
        self.pose = payload2tuple(
            extract_payload_from_messages(
                self.pose_fb_code, 
                messages
            )
        )
