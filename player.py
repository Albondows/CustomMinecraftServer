import packet
import struct

class Player:
    FORMAT_VERSION = 1
    
    def __init__(self, username: str, connection, rank = 0):
        self.username   = username
        self.connection = connection

        self.player_id  = 0
        self.world      = ""
        
        self.x          = 0
        self.y          = 0
        self.z          = 0

        self.c_packets = dict(packet.client_packets)
        self.s_packets = dict(packet.server_packets)

    def send_bytes(self, data):
        self.connection.send(data)

    def send_packet(self, packet: packet.Packet):
        self.send_bytes(packet.to_bytes())
    
    def read_packet(self) -> packet.Packet:
        packet_id = int.from_bytes(self.read_bytes(1), byteorder = "big")
        
        if packet_id in self.c_packets:
            packet_  = self.c_packets[packet_id]
            return packet_.from_bytes(packet_id.to_bytes(1, byteorder="big") + self.read_bytes(packet_.size - 1))
        else:
            self.send_packet(packet.DisconnectPacket(f"Invalid packet {packet_id}!"))
            return None
        
    def read_bytes(self, num):
        data = self.connection.recv(num)

        while len(data) < num:
            data += self.connection.recv(num)

        return data

    def message(self, msg):
        self.send_packet(packet.MessagePacket(0, msg))

    def dump(self):
        return struct.pack("!B 64s h", self.FORMAT_VERSION, self.username.encode("cp437"), self.rank)

    @classmethod
    def undump(cls, data):
        version = int.from_bytes(data[0])

        if version == 1:
            _, username, rank = struct.unpack("!B 64s h", data)
            username = username.decode("cp437").replace("\x00", "")

            this_player = cls(username=username, connection=None, rank=rank)
        else:
            raise ValueError(f"Unsuported format version {version}")
