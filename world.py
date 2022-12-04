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
    
        self.blocks = generator(self.width, self.height, self.length, 0)
    
    def get_block(self, x: int, y: int, z: int):
        return self.blocks[x + (self.width * z) + (self.width, self.length * z)] # The blocks are stored in XZY order

    def set_block(self, x: int, y: int, z: int, block_type: block.Block):
        self.blocks[x + (self.width * z) + (self.width * self.length * y)] = block_type # The blocks are stored in XZY order

    def send(self, player: player.Player):
        player.send_packet(packet.ServerIdentificationPacket(7, self.name, self.motd, 0x64))
        player.send_packet(packet.LevelInitilizePacket())

        data = (self.width * self.height * self.length).to_bytes(4, byteorder="big") \
             + bytearray([int(i) for i in self.blocks])
        
        data = gzip.compress(data)

        for i in range(0, len(data), 1024):
            player.send_packet(packet.LevelDataChunkPacket(min(1024, len(data)-i), data[i:i+1023], 247))
        
        player.send_packet(packet.LevelFinalizePacket(self.width, self.height, self.length))
        player.send_packet(packet.PositionOrientationPacket(255, self.width//2*32, (self.height//2*32)+51, self.length//2*32, 0, 0))
    
    def dump(self):
        return struct.pack("!B 64s 64s hhh", self.FORMAT_VERSION, self.name.encode("cp437"), self.motd.encode("cp437"),
                                             self.width, self.height, self.length) \
                           + bytearray([i.to_bytes() for i in self.blocks]) \
                           + bytearray([i.to_bytes_extra() for i in self.blocks])

