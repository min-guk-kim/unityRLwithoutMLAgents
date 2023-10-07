import socket
import struct

# TODO: converting timeScale value by using Python.

class UnityCommunication:
    def __init__(self, host="127.0.0.1", port=25001):
        self.host = host
        self.port = port
        self.sock = None
        
    def send_position(self, agent_pos):
        """
        Sends the agent's position to Unity via TCP and receives the updated position from Unity.

        Parameters:
        - agent_pos (list): A list containing the x and z coordinates of the agent's position.

        Returns:
        - list: A list containing the updated x and z coordinates received from Unity.
        """

        # Convert the agent's x, y (which is always 0 in this context), and z positions into bytes
        posBytes = struct.pack('fff', agent_pos[0], 0.0, agent_pos[1])

        # Send the packed position bytes to Unity via socket
        self.sock.sendall(posBytes)

        # Receive the updated position data from Unity
        receivedData = self.sock.recv(12)

        # Unpack the received bytes to get the updated x, y, and z coordinates of the agent's position
        x, _, z = struct.unpack('fff', receivedData)

        # Return the updated x and z coordinates as a list
        return [x, z]


    def connect_and_check_unity(self):
        """
        Establishes a connection with Unity and continuously checks the connection.
        If the connection is lost, closes the socket.
        """
        try:
            if self.sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                print("Successfully connected to Unity!")
                return True
            else:
                return self.connection_check()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def connection_check(self):
        """
        Checks if the connection to Unity is active.
        If not, closes the socket.
        """
        try:
            self.sock.settimeout(0.1)
            self.sock.sendall(b'PING')
            response = self.sock.recv(12).decode("UTF-8")

            if response == 'DISCONNECTED':
                print("Disconnected with Unity")
                self.sock.close()
                self.sock = None
            elif response == 'PONG':
                print("Connection to Unity is still active.")
                return True
        except socket.error as e:
            print(f"Connection to Unity is lost. Reason: {e}")
            self.sock.close()
            self.sock = None

    def send_message_training_over(self):
        """
        Sends a message to Unity indicating the training is finished.
        """
        self.sock.sendall(b'endOfTraining')
        print("Sent a message that the training is finished.")
        print("Built File will be quited (in case of Unity editor, play mode will be quited).")
