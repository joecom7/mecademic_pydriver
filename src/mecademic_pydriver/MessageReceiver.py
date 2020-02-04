import select
from requests import ConnectionError


class MessageReceiver:
    """
    Class to handle messages over socket using a message_terminator
    """

    def __init__(self, socket, message_terminator="\x00"):
        """
        Constructor
        socket : socket to use
        message_terminator : terminator of the message
        """
        self.socket = socket
        self.buffer = ""
        self.messages = []
        self.message_terminator = message_terminator

    def wait_for_new_messages(self, timeout=None):
        """
        Wait for new messages in the socket
        timeout : same meaning of select.select
        """
        if timeout:
            _, _, _ = select.select([self.socket], [], [], timeout)
        else:
            _, _, _ = select.select([self.socket], [], [])

    def bytes_available(self):
        """
        Check if bytes are available on the socket
        """
        # A socket becomes ready for reading when
        # 1) someone connects after a call to listen
        #   (which means that accept won't block),
        # or
        # 2) data arrives from the remote end,
        # or
        # 3) the socket is closed or reset
        #   (in this case, recv will return an empty string).
        rlist, _, _ = select.select([self.socket], [], [], 0)  # 0=poll
        if not rlist:
            return False
        else:
            return True

    def __recv_internal(self, bufsize=4096):
        """
        Internal function
        Receive bytes from socket and add them in the buffer
        """
        # recv data from socket
        local_buffer = self.socket.recv(bufsize).decode("ascii")
        if len(local_buffer) == 0:
            # The other side has shut down the socket.
            # You'll get 0 bytes of data.
            # 0 means you will never get more data on that socket.
            # But if you keep asking for data, you'll keep getting 0 bytes.
            raise ConnectionError(
                "messageReceiver::recv : received a zero-len buffer")

        # update the local buffer
        self.buffer += local_buffer

    def recv(self, bufsize=4096):
        """
        Recv msg from socket, update buffer and messages
        return: number of messages in the queue
        """

        # check if socket is available for reading
        if(not self.bytes_available()):
            return len(self.messages)

        self.__recv_internal(bufsize)

        return self.parse_buffer()

    def recv_all(self, bufsize=4096):
        """
        receive and parse all messages from the socket
        """
        while(self.bytes_available()):
            self.__recv_internal(bufsize)

        return self.parse_buffer()

    def parse_buffer(self):
        """
        parse the buffer and append new messages to self.messages
        return: number of messages in the queue
        """
        while len(self.buffer) is not 0:

            msg, ignored, self.buffer = self.buffer.partition(
                self.message_terminator)
            if not ignored:
                # if not terminator char, reappend msg in baffer (last message was not compleately received)
                self.buffer = msg + self.buffer
                break

            # append parsed message to messages
            self.messages.append(msg)

        return len(self.messages)

    def clear_buffer(self):
        """
        Clean the recv buffer and stored messages
        """
        self.recv_all()
        self.buffer = ""
        self.messages = []

    def get_message(self, recv=True):
        """
        Get the older message in the queue
        Return None if no messages are in the queue
        recv : bool (default True)
            If true: call self.recv()
        """
        if recv:
            self.recv()

        if self.messages:
            return self.messages.pop(0)
        else:
            return None

    def get_all_messages(self, recv_all=True):
        """
        Get all messages from the queue
        Messages are ordered starting from the older
        Return [] if no messages are in the queue
        recv_all : bool (default True)
            If true: call self.recv_all()
        """
        if recv_all:
            self.recv_all()

        messages = self.messages
        self.messages = []
        return messages

    def get_last_message(self, recv_all=True, discard_previous_msgs=True):
        """
        Get the last (newer) message in the queue
        Return None if no messages are in the queue
        recv_all : bool (default True)
            If true: call self.recv_all()
        discard_previous_msgs: bool (default True)
            Clear other messages
        """
        if recv_all:
            self.recv_all()

        if self.messages:
            msg = self.messages.pop(-1)
            if discard_previous_msgs:
                self.messages = []
            return msg
        else:
            return None

    def get_last_messages(self, num_messages, recv_all=True, discard_previous_msgs=True):
        """
        Get the last num_messages messages in the queue
        Messages are ordered starting from the older
        Return a list of messages
        The list can be shorter than num_messages if less messages are available
        recv_all : bool (default True)
            If true: call self.recv_all()
        discard_previous_msgs: bool (default True)
            Clear other messages
        """
        if recv_all:
            self.recv_all()

        messages = []
        for _ in range(0, num_messages):
            if self.messages:
                messages.append(self.messages.pop(-1))
            else:
                break

        messages.reverse()

        if discard_previous_msgs:
            self.messages = []

        return messages
