import packet
import struct
import rank

class Player:
    FORMAT_VERSION = 1
    
    def __init__(self, username: str, connection):
        self.username                = username
        self.rank                    = rank

        self.connection              = connection

        self.player_id               = 0
        self.world                   = ""
        
        self.x                       = 0
        self.y                       = 0
        self.z                       = 0

        self.logins                  = 0
        self.blocks_mined            = 0
        self.blocks_placed           = 0
        self.blocks_modified_session = 0

        self.c_packets = dict(packet.client_packets)
        self.s_packets = dict(packet.server_packets)
    
    def format_r(self, text):
        return text.replace("§nme", self.username) \
                   .replace("§nck", self.username) \
                   .replace("§clr", "&7") \
                   .replace("§lim", "Connected") \
                   .replace("§lom", "Disconnected") \
                   .replace("§rnm", self.rank.name) \
                   .replace("§rcl", self.rank.color) \
                   .replace("§rnb", str(self.rank.num))

    
    def format_s(self, text):
        return text.replace("§snm", self.username) \
                   .replace("§snk", self.username) \
                   .replace("§scl", "&7") \
                   .replace("§sli", "Connected") \
                   .replace("§slo", "Disconnected") \
                   .replace("§srn", self.rank.name) \
                   .replace("§src", self.rank.color) \
                   .replace("§srb", str(self.rank.num))

    def send_bytes(self, data):
        self.connection.send(data)
    
    def read_packet(self) -> tuple:
        packet_id = int.from_bytes(self.read_bytes(1), byteorder = "big")
        
        if packet_id in self.c_packets:
            packet_  = self.c_packets[packet_id]
            return packet_.from_bytes(packet_id.to_bytes(1, byteorder="big", signed=False) + self.read_bytes(packet_.size - 1))
        else:
            self.send_bytes(packet.disconnect_packet.to_bytes(f"Invalid packet {packet_id}!"))
            return tuple()
        
    def read_bytes(self, num):
        data = self.connection.recv(num)

        while len(data) < num:
            data += self.connection.recv(num)

        return data

    def _message(self, msg:str):
        if len(msg) > 64:
            self._message(msg[:64])
            self._message("> " + msg[64:])
            return

        self.send_bytes(packet.message_packet.to_bytes(0, msg))

    def to_bytes(self):
        return struct.pack("!B 64s h i i i", self.FORMAT_VERSION, self.username.encode("cp437"), self.rank.num, self.logins, self.blocks_mined, self.blocks_placed)

    @classmethod
    #                         vvvvv The player module dosen't have access to the server object.
    def from_bytes(cls, data, ranks):
        version = data[0]

        if version == 1:
            _, username, ranknum, logins, blocks_mined, blocks_placed = struct.unpack("!B 64s h i i i", data)
            username = username.decode("cp437").replace("\x00", "")

            this_player = cls(username=username, connection=None)
            this_player.rank = ranks[max(i for i in ranks if i in ranks and i <= ranknum)]
            
            this_player.logins = logins
            this_player.blocks_mined = blocks_mined
            this_player.blocks_placed = blocks_placed
            
            return this_player
        else:
            raise ValueError(f"Unsuported format version {version}")
