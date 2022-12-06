import struct
import typing

class InvalidPacketError(Exception):
    pass

def string_to_bytes(string):
    return f"{string: <64}".encode("cp437")

def bytes_to_string(string):
    return string.decode("cp437").strip()

def get_size(augment: str):
    #                     vvv adding a space because the i variable dosent contain the space that is used to separate the fields
    #                     vvv                  vvvv removing the first character because the augment starts with '!' (network order)
    return sum([SIZES[i + " "] for i in augment[1:].split(" ") if i])

BYTE                   = "B "
BYTE_SIZE              = 1
SIGNED_BYTE            = "b "
SIGNED_BYTE_SIZE       = 1
FIXED_POINT_BYTE       = "b "
FIXED_POINT_BYTE_SIZE  = 1
SIGNED_SHORT           = "h "
SIGNED_SHORT_SIZE      = 2
FIXED_POINT_SHORT      = "h "
FIXED_POINT_SHORT_SIZE = 2
STRING                 = "64s "
STRING_SIZE            = 64
BYTE_ARRAY             = "1024s "
BYTE_ARRAY_SIZE        = 1024

SIZES = {
    BYTE: BYTE_SIZE,
    SIGNED_BYTE: SIGNED_BYTE_SIZE,
    FIXED_POINT_BYTE: FIXED_POINT_BYTE_SIZE,
    SIGNED_SHORT: SIGNED_SHORT_SIZE,
    FIXED_POINT_SHORT: FIXED_POINT_SHORT_SIZE,
    STRING: STRING_SIZE,
    BYTE_ARRAY: BYTE_ARRAY_SIZE,
}

class Packet:
    def __init__(self, packet_id: int, augment: str):
        self.packet_id = packet_id
        self.augment   = "!" + augment
        self.size      = get_size(self.augment)

    def to_bytes(self, *args):
        return struct.pack(self.augment, self.packet_id, *[
            string_to_bytes(i) if isinstance(i, str) else i
            for i in args
        ])

    def from_bytes(self, data) -> list[typing.Any]:
        if data[0] != self.packet_id:
            raise InvalidPacketError(f"First byte of the packet must be {self.packet_id} but it's {data[0]}")
        
        return [bytes_to_string(i) if isinstance(i, bytes) and len(i) == 64 else i
                for i in struct.unpack(self.augment, data)]

player_identification_packet         = Packet(packet_id=0x00, augment=BYTE + BYTE + STRING + STRING + BYTE)
server_identification_packet         = Packet(packet_id=0x00, augment=BYTE + BYTE + STRING + STRING + BYTE)
ping_packet                          = Packet(packet_id=0x01, augment=BYTE)
level_initilize_packet               = Packet(packet_id=0x02, augment=BYTE)
level_data_chunk_packet              = Packet(packet_id=0x03, augment=BYTE + SIGNED_SHORT + BYTE_ARRAY + BYTE)
level_finalize_packet                = Packet(packet_id=0x04, augment=BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT)
client_set_block_packet              = Packet(packet_id=0x05, augment=BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE + BYTE)
server_set_block_packet              = Packet(packet_id=0x06, augment=BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE)
spawn_player_packet                  = Packet(packet_id=0x07, augment=BYTE + BYTE + STRING + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE + BYTE)
position_orientation_packet          = Packet(packet_id=0x08, augment=BYTE + BYTE + SIGNED_SHORT + SIGNED_SHORT + SIGNED_SHORT + BYTE + BYTE)
relative_position_orientation_packet = Packet(packet_id=0x09, augment=BYTE + BYTE + BYTE + BYTE + BYTE + BYTE + BYTE)
relative_position_packet             = Packet(packet_id=0x0a, augment=BYTE + BYTE + BYTE + BYTE + BYTE + BYTE + BYTE)
relative_orientation_packet          = Packet(packet_id=0x0b, augment=BYTE + BYTE + BYTE + BYTE)
despawn_player_packet                = Packet(packet_id=0x0c, augment=BYTE + BYTE)  
message_packet                       = Packet(packet_id=0x0d, augment=BYTE + BYTE + STRING)
disconnect_packet                    = Packet(packet_id=0x0e, augment=BYTE + STRING)
change_player_type_packet            = Packet(packet_id=0x0f, augment=BYTE + BYTE)

client_packets = {
    0x00: player_identification_packet,
    0x05: client_set_block_packet,
    0x08: position_orientation_packet,
    0x0d: message_packet,
}

server_packets = {
    0x00: server_identification_packet,
    0x01: ping_packet,
    0x02: level_initilize_packet,
    0x03: level_data_chunk_packet,
    0x04: level_finalize_packet,
    0x06: server_set_block_packet,
    0x07: spawn_player_packet,
    0x08: position_orientation_packet,
    0x09: relative_position_orientation_packet,
    0x0a: relative_position_packet,
    0x0b: relative_orientation_packet,
    0x0c: despawn_player_packet,
    0x0d: message_packet,
    0x0e: disconnect_packet,
    0x0f: change_player_type_packet,
}