class Packet:
    """
    Packet when something not defined has to be handled
    Acceptable task_types:

     - READY: A Client is ready to start a game
        Additional Data:
         None
    """
    def __init__(self, task_type: str, **kwargs):
        self.task_type = task_type
        self.data = kwargs

    def __str__(self):
        return f'<Packet task_type: "{self.task_type}">'


class GamePacket(Packet):
    """
    GamePackets to handle during a game
    Acceptable task_types:

     - READY: A Client is ready to start a game
        Additional Data:
         None
     - USER: A Client sent the node and is receiving his User
        Additional Data:
         - user: The User object of the Client
     - USER_LOG: The Client logged in and is now receiving his User
        Additional Data:
         - user: The User object of the Client
     - USER_REG: A Client registered a new user and is not receiving his new User
        Additional Data:
         - user: The User object of the Client
     - USER_DUM: A Client requested a Dummy and is now receiving his User
        Additional Data:
         - user: The User object of the Client
    """
    def __init__(self, task_type: str, **kwargs):
        super().__init__(task_type, **kwargs)

    def __str__(self):
        return f'<GamePacket task_type: "{self.task_type}">'


class UserUpdatePacket(Packet):
    """
    Packet when a User wants to update his own User
    Acceptable task_types:

     - NODE_R: Client returns his node to receive a User to his node
        Additional Data:
         - node: the node of the client (uuid.get_node())
     - LOGIN: User logged in to a registered account
        Additional Data:
         - username: The Username to the Client
         - password: The Password to the Client
     - REGISTER: Registers a new Client with the following arguments
        Additional Data:
         - uuid: The current UUID of the new Client (uuid.uuid1())
         - username: The Username of the new Client
         - email: The Email of the new Client
         - password: The Password of the new Client
     - DUMMY: The Client is requesting a temporary Dummy account
        Additional Data:
         - uuid: The current UUID of the new Client (uuid.uuid1())
         - name: The name of the Dummy
     - LOGOUT: A Client requests a Logout from the current Account
        Additional Data:
         None
    """
    def __init__(self, task_type: str, **kwargs):
        super().__init__(task_type, **kwargs)

    def __str__(self):
        return f'<UserUpdatePacket task_type: "{self.task_type}">'
