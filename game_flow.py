import random
import socket
import struct
import uuid


STRUCT_FORMAT = 'Ii'

CLIENT_STR = f"client_id_{random.randint(1, 100)}"

def send_message(sock: socket.socket, msg_type: int, data):
    serialized_data = data.serialize()
    header = MessageHeader(msg_type, len(serialized_data)).serialize()
    sock.sendall(header + serialized_data)


class MessageHeader:
    FORMAT = "Ii"

    def __init__(self, msg_type: int, size: int):
        self.msg_type = msg_type
        self.size = size

    def serialize(self) -> bytes:
        return struct.pack(self.FORMAT, self.msg_type, self.size)

    @staticmethod
    def deserialize(data: bytes):
        msg_type, size = struct.unpack(MessageHeader.FORMAT, data)
        return MessageHeader(msg_type, size)


class ClientsList:
    def __init__(self, cmd="", uuids=None):
        if uuids is None:
            uuids = []
        self.cmd = cmd[:128]
        self.uuids = uuids

    def serialize(self):
        serialized_cmd = self.cmd.encode('utf-8').ljust(128, b'\0')
        uuids_data = b''.join([uuid.encode('utf-8') + b'\0' for uuid in self.uuids])
        return serialized_cmd + uuids_data

    @staticmethod
    def deserialize(data):
        cmd = struct.unpack('128s', data[:128])[0]
        uuids = []
        offset = 128
        for i in range(5):
            uuid = struct.unpack('15s', data[offset:offset + 15])[0]
            uuids.append(uuid.decode().rstrip("\0"))
            offset += 15
        client_list = ClientsList()
        client_list.cmd = cmd
        client_list.uuids = uuids
        return client_list

    @staticmethod
    def populate_with_clients(clients_map, client_list):
        client_list.uuids = list(clients_map.keys())

    def __str__(self):
        return f"Command: {self.cmd}, UUIDs: {', '.join(self.uuids)}"
    

class RoomData:
    def __init__(self, room_name='', joined_uuid='', members=None):
        if members is None:
            members = []
        self.room_name = room_name[:128]
        self.joined_uuid = joined_uuid[:48]
        self.members = members[:5] + [''] * (5 - len(members))

    def serialize(self):
        serialized_cmd = self.room_name.encode('utf-8').ljust(128, b'\0')
        serialized_join = self.joined_uuid.encode('utf-8').ljust(48, b'\0')
        uuids_data = b''.join([member.encode('utf-8').ljust(48, b'\0') for member in self.members])
        print(serialized_join)
        return serialized_cmd + serialized_join + uuids_data

    @staticmethod
    def deserialize(data):
        print(data)
        if len(data) < 128 + 48 + 5 * 48:
            raise ValueError("Not enogh")

        room_name = struct.unpack('128s', data[:128])[0].decode('utf-8').rstrip('\0')
        joined_uuid = struct.unpack('48s', data[128:128+48])[0].decode('utf-8').rstrip('\0')

        uuids = []
        offset = 128 + 48
        for _ in range(5):
            uuid = struct.unpack('48s', data[offset:offset + 48])[0].decode('utf-8').rstrip('\0')
            uuids.append(uuid)
            offset += 48

        return RoomData(room_name, joined_uuid, uuids)
    
    def __repr__(self):
        return f"Room name: {self.room_name}, Joined: {self.joined_uuid}, List of mambers: {self.members}"


class UserData:
    def __init__(self, counter=0, user_msg=''):
        self.counter = counter
        self.user_msg = user_msg.encode('utf-8')[:128]

    def serialize(self):
        return struct.pack(STRUCT_FORMAT, self.counter, self.user_msg.encode())
    
    def __repr__(self):
        return f"Counter: {self.counter}, Massage: {self.user_msg}"

    @classmethod
    def deserialize(cls, data):
        try:
            unpacked_data = struct.unpack(STRUCT_FORMAT, data)
            return cls(unpacked_data[0], unpacked_data[1].decode('utf-8').rstrip('\x00'))  # Убираем возможные нулевые символы
        except Exception as e:
            print(e)


class Greeting:
    FORMAT = "128s128s"

    def __init__(self, msg: str = "", uuid: str = ""):
        self.msg = msg.encode('utf-8')[:127].ljust(128, b'\0')
        self.uuid = uuid.encode('utf-8')[:127].ljust(128, b'\0')  

    def serialize(self) -> bytes:
        return struct.pack(self.FORMAT, self.msg, self.uuid)

    @staticmethod
    def deserialize(data: bytes):
        print(data)
        msg, uuid = struct.unpack(Greeting.FORMAT, data)
        s_msg = msg.decode('utf-8').rstrip('\0')
        try:
            s_uuid = uuid.decode('utf-8').rstrip('\0')
        except:
            s_uuid = ""
        return Greeting(s_msg, s_uuid)

    def __str__(self):
        return f"msg: {self.msg.decode('utf-8').rstrip()}, uuid: {self.uuid}"
