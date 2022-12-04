from os import stat
import struct

class InvalidPacketError(Exception):
    pass

def string_to_bytes(string):
    return f"{string: <64}".encode("cp437")

def bytes_to_string(string):
    return string.decode("cp437").strip()

BYTE                   = "B"
BYTE_SIZE              = 1
SIGNED_BYTE            = "b"
SIGNED_BYTE_SIZE       = 1
FIXED_POINT_BYTE       = "b"
FIXED_POINT_BYTE_SIZE  = 1
SHORT                  = "H" # Unused
SHORT_SIZE             = 2
SIGNED_SHORT           = "h"
SIGNED_SHORT_SIZE      = 2
FIXED_POINT_SHORT      = "h"
FIXED_POINT_SHORT_SIZE = 2
INT                    = "I" # Unused
INT_SIZE               = 4
SIGNED_INT             = "i" # Unused
SIGNED_INT_SIZE        = 4
FIXED_POINT_INT        = "i" # Unused
FIXED_POINT_INT_SIZE   = 4
STRING                 = "64s"
STRING_SIZE            = 64
BYTE_ARRAY             = "1024s"
BYTE_ARRAY_SIZE        = 1024

class Packet:
    packet_id = 0x00

    def __init__(self):
        pass

    def to_bytes(self):
        return struct.pack("B", self.packet_id)

    @classmethod
    def from_bytes(cls, data):
        return cls()

class PlayerIdentificationPacket(Packet):
    packet_id = 0x00
    size      = BYTE_SIZE + BYTE_SIZE + STRING_SIZE + STRING_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + STRING + STRING + BYTE

    def __init__(self, version, username, mppass, is_cpe):
        self.version  = version
        self.username = username
        self.mppass   = mppass
        self.is_cpe   = is_cpe

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.version, string_to_bytes(self.username), string_to_bytes(self.mppass), self.is_cpe)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, version, username, mppass, is_cpe = struct.unpack(cls.augment, data)
        username = bytes_to_string(username)
        mppass = bytes_to_string(mppass)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(version, username, mppass, is_cpe)

class ServerIdentificationPacket(Packet):
    packet_id = 0x00
    size      = BYTE_SIZE + BYTE_SIZE + STRING_SIZE + STRING_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + STRING + STRING + BYTE

    def __init__(self, version, name, motd, is_op):
        self.version = version
        self.name    = name
        self.motd    = motd
        self.is_op   = is_op

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.version, string_to_bytes(self.name), string_to_bytes(self.motd), self.is_op)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, version, name, motd, is_op = struct.unpack(cls.augment, data)
        name = bytes_to_string(name)
        key  = bytes_to_string(key)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(version, name, motd, is_op)

class PingPacket(Packet):
    packet_id = 0x01
    size      = BYTE_SIZE
    augment   = "!" + BYTE

    def __init__(self):
        pass

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id = struct.unpack(cls.augment, data)[0] # [0] bc struct.unpack returns a list even if theres only 1 

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls()

class LevelInitilizePacket(Packet):
    packet_id = 0x02
    size      = BYTE_SIZE
    augment   = "!" + BYTE

    def __init__(self):
        pass

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:  
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls()

class LevelDataChunkPacket(Packet):
    packet_id = 0x03
    size      = BYTE_SIZE + SIGNED_SHORT_SIZE + BYTE_ARRAY_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + SIGNED_SHORT + BYTE_ARRAY + BYTE

    def __init__(self, length, data, percent):
        self.length  = length
        self.data    = data
        self.percent = percent

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.length, self.data + (b"\x00" * (1024 - len(self.data))), self.percent)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, length, data, percent = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(length, data, percent)

class LevelFinalizePacket(Packet):
    packet_id = 0x04
    size      = BYTE_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE
    augment   = "!" + BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT

    def __init__(self, width, height, length):
        self.width  = width
        self.height = height
        self.length = length

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.width, self.height, self.length)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, width, height, length = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(width, height, length)

class ClientSetBlockPacket(Packet):
    packet_id = 0x05
    size      = BYTE_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE + BYTE

    def __init__(self, x, y, z, mode, block):
        self.x     = x
        self.y     = y
        self.z     = z
        self.mode  = mode
        self.block = block

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.x, self.y, self.z, self.mode, self.block)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, x, y, z, mode, block = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(x, y, z, mode, block)

class ServerSetBlockPacket(Packet):
    packet_id = 0x06
    size      = BYTE_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE

    def __init__(self, x, y, z, block):
        self.x     = x
        self.y     = y
        self.z     = z
        self.block = block

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.x, self.y, self.z, self.block)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, x, y, z, block = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(x, y, z, block)

class SpawnPlayerPacket(Packet):
    packet_id = 0x07
    size      = BYTE_SIZE + BYTE_SIZE + STRING_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + STRING + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE + BYTE

    def __init__(self, player_id, username, x, y, z, pitch, yaw):
        self.player_id = player_id
        self.username  = username
        self.x         = x
        self.y         = y
        self.z         = z
        self.pitch     = pitch
        self.yaw       = yaw

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id, string_to_bytes(self.username), self.x, self.y, self.z, self.pitch, self.yaw)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id, username, x, y, z, pitch, yaw = struct.unpack(cls.augment, data)

        username = bytes_to_string(username)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id, username, x, y, z, pitch, yaw)

class PositionOrientationPacket(Packet):
    packet_id = 0x08
    size      = BYTE_SIZE + BYTE_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + SIGNED_SHORT_SIZE + BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE + BYTE

    def __init__(self, player_id, x, y, z, pitch, yaw):
        self.player_id = player_id
        self.x         = x
        self.y         = y
        self.z         = z
        self.pitch     = pitch
        self.yaw       = yaw

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id, self.x, self.y, self.z, self.pitch, self.yaw)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id, x, y, z, pitch, yaw = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id, x, y, z, pitch, yaw)

class RelativePositionOrientationPacket(Packet):
    packet_id = 0x09
    size      = BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + BYTE + BYTE + BYTE + BYTE + BYTE

    def __init__(self, player_id, x, y, z, pitch, yaw):
        self.player_id = player_id
        self.x         = x
        self.y         = y
        self.z         = z
        self.pitch     = pitch
        self.yaw       = yaw

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id, self.x, self.y, self.z, self.pitch, self.yaw)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id, x, y, z, pitch, yaw = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id, x, y, z, pitch, yaw)

class RelativePositionPacket(Packet):
    packet_id = 0x0a
    size      = BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + BYTE + BYTE + BYTE + BYTE + BYTE

    def __init__(self, player_id, x, y, z):
        self.player_id = player_id
        self.x         = x
        self.y         = y
        self.z         = z

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id, self.x, self.y, self.z)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id, x, y, z = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id, x, y, z)

class RelativeOrientationPacket(Packet):
    packet_id = 0x0b
    size      = BYTE_SIZE + BYTE_SIZE + BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE + BYTE + BYTE

    def __init__(self, player_id, pitch, yaw):
        self.player_id = player_id
        self.pitch     = pitch
        self.yaw       = yaw

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id, self.pitch, self.yaw)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id, pitch, yaw = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id, pitch, yaw)

class DespawnPlayerPacket(Packet):
    packet_id = 0x0c
    size      = BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE

    def __init__(self, player_id):
        self.player_id = player_id

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id)
    
class MessagePacket(Packet):
    packet_id = 0x0d
    size      = BYTE_SIZE + BYTE_SIZE + STRING_SIZE
    augment   = "!" + BYTE + BYTE + STRING

    def __init__(self, player_id, message):
        self.player_id = player_id
        self.message   = message

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.player_id, string_to_bytes(self.message))

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, player_id, message = struct.unpack(cls.augment, data)

        message = bytes_to_string(message)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(player_id, message)

class DisconnectPacket(Packet):
    packet_id = 0x0e
    size      = BYTE_SIZE + STRING_SIZE
    augment   = "!" + BYTE + STRING

    def __init__(self, reason):
        self.reason   = reason

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, string_to_bytes(self.reason))

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, reason = struct.unpack(cls.augment, data)

        reason = bytes_to_string(reason)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(reason)

class ChangePlayerTypePacket(Packet):
    packet_id = 0x0f
    size      = BYTE_SIZE + BYTE_SIZE
    augment   = "!" + BYTE + BYTE

    def __init__(self, new_type):
        self.new_type = new_type

    def to_bytes(self):
        return struct.pack(self.augment, self.packet_id, self.new_type)

    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes):
            raise TypeError(f"data must be bytes-like object, not {type(data)}")
        if len(data) != cls.size:
            raise ValueError(f"data must be {cls.size} bytes")
        
        packet_id, new_type = struct.unpack(cls.augment, data)

        if packet_id != cls.packet_id:
            raise InvalidPacketError(f"Packet ID must be {cls.packet_id}")
        
        return cls(new_type)

client_packets = {
    0x00: PlayerIdentificationPacket,
    0x05: ClientSetBlockPacket,
    0x08: PositionOrientationPacket,
    0x0d: MessagePacket,
}

server_packets = {
    0x00: ServerIdentificationPacket,
    0x01: PingPacket,
    0x02: LevelInitilizePacket,
    0x03: LevelDataChunkPacket,
    0x04: LevelFinalizePacket,
    0x06: ServerSetBlockPacket,
    0x07: SpawnPlayerPacket,
    0x08: PositionOrientationPacket,
    0x09: RelativePositionOrientationPacket,
    0x0a: RelativePositionPacket,
    0x0b: RelativeOrientationPacket,
    0x0c: DespawnPlayerPacket,
    0x0d: MessagePacket,
    0x0f: ChangePlayerTypePacket,
}