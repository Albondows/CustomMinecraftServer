import gzip
import struct

import player
import packet
import block
import world_generator

class World:
    FORMAT_VERSION = 1

    def __init__(self, width: int, height: int, length: int, name: str, motd="Welcome!", generator=world_generator.flat_world_generator):
        self.width  = width
        self.height = height
        self.length = length
        
        self.name   = name
        self.motd   = motd
    
        self.blocks = bytearray(generator(self.width, self.height, self.length, 0))
    
    def get_block(self, x: int, y: int, z: int):
        index = x + (self.width * z) + (self.width * self.length * z)  # The blocks are stored in XZY order
        return int.from_bytes(self.blocks[index:index + 1], byteorder="big")

    def set_block(self, x: int, y: int, z: int, block_id: block.block_id_type):
        index = x + (self.width * z) + (self.width * self.length * z)  # The blocks are stored in XZY order
        self.blocks[index*2:index*2+1] = bytearray(block_id.to_bytes(2, byteorder="big", signed=False))
    
    def send(self, player: player.Player):
        player.send_bytes(packet.server_identification_packet.to_bytes(7, self.name, self.motd, 0x64))
        player.send_bytes(packet.level_initilize_packet.to_bytes())

        data = (self.width * self.height * self.length).to_bytes(4, byteorder="big") \
             + bytearray([i for i in self.blocks[1::2]])
        
        data = gzip.compress(data)

        for i in range(0, len(data), 1024):
            player.send_bytes(packet.level_data_chunk_packet.to_bytes(min(1024, len(data)-i), data[i:i+1023], 247))
        
        player.send_bytes(packet.level_finalize_packet.to_bytes(self.width, self.height, self.length))
        player.send_bytes(packet.position_orientation_packet.to_bytes(255, self.width//2*32, (self.height//2*32)+51, self.length//2*32, 0, 0))
    
    def to_bytes(self):
        return struct.pack("!B 64s 64s hhh", self.FORMAT_VERSION, self.name.encode("cp437"), self.motd.encode("cp437"),
                                             self.width, self.height, self.length) \
                           + bytes(self.blocks)

    @classmethod
    def from_bytes(cls, data):
        format_version = data[0]

        if format_version == 1:
            name, motd, width, height, length = struct.unpack("!64s 64s hhh", data[1:135])
            name = name.decode("cp437").replace("\x00", " ").strip()
            motd = motd.decode("cp437").replace("\x00", " ").strip()

            extra_data  = data[135+(width*height*length*2):]

            this_world = cls(width=width, height=height, length=length, name=name, motd=motd, generator=lambda width, height, length, seed: b'')
            this_world.blocks = bytearray(data[135:135+(width*height*length*2)])
            #                                                               ^ 2 because every block ID is 2 bytes

            '''i = 0
            while True:
                position = int.from_bytes(extra_data[i:i+4], byteorder="big", signed=True)

                if position == -1:
                    break
                    
                this_world.blocks[position].from_bytes_extra(extra_data[i+4:i+4+this_world.blocks[position].extra_data_size])'''
            
            return this_world
        
        else:
            raise ValueError(f"Unsuported format version {format_version}")