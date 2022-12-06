import constants

COLLIDE_AIR = 0
COLLIDE_SWIM = 1
COLLIDE_SOLID = 2
COLLIDE_SLIPERRY = 3
COLLIDE_MORE_SLIPERRY = 4
COLLIDE_WATER = 5
COLLIDE_LAVA = 6
COLLIDE_ROPE = 7

SOUND_NONE = 0
SOUND_WOOD = 1
SOUND_GRAVEL = 2
SOUND_GRASS = 3
SOUND_STONE = 4
SOUND_METAL = 5
SOUND_GLASS = 6
SOUND_WOOL = 7
SOUND_SAND = 8
SOUND_SNOW = 9

BLOCK_DRAW_SOLID = 0
BLOCK_DRAW_GLASS = 1
BLOCK_DRAW_LEAVES = 2
BLOCK_DRAW_AIR = 3

class BlockType:
    def __init__(self, block_id, name="Invalid", min_rank=0, fallback=0,
                 is_cube=True, collide=COLLIDE_SOLID, speed=1.0,
                 toptex=0, lefttex=0, righttex=0, fronttex=0, backtex=0, bottomtex=0,
                 blocks_light=True, sound=SOUND_STONE, makes_light=True,
                 minx=0, miny=0, minz=0, maxx=16, maxy=16, maxz=16,
                 block_draw=BLOCK_DRAW_SOLID, fog_density=0.0,
                 fog_red=0, fog_green=0, fog_blue=0):

        self.block_id     = block_id
        self.name         = name
        self.min_rank     = min_rank
        self.fallback     = fallback
        self.is_cube      = is_cube
        self.collide      = collide
        self.speed        = speed
        self.toptex       = toptex
        self.lefttex      = lefttex
        self.righttex     = righttex
        self.fronttex     = fronttex
        self.backtex      = backtex
        self.bottomtex    = bottomtex
        self.blocks_light = blocks_light
        self.sound        = sound
        self.makes_light  = makes_light
        self.minx         = minx
        self.miny         = miny
        self.minz         = minz
        self.maxx         = maxx
        self.maxy         = maxy
        self.maxz         = maxz
        self.block_draw   = block_draw
        self.fog_density  = fog_density
        self.fog_red      = fog_red
        self.fog_green    = fog_green
        self.fog_blue     = fog_blue

air_block     = BlockType(block_id=0, name="Air",         min_rank=constants.RANK_GUEST,    fallback=0,                collide=COLLIDE_AIR,                                                                                                  block_draw=BLOCK_DRAW_AIR  )
stone_block   = BlockType(block_id=1, name="Stone",       min_rank=constants.RANK_GUEST,    fallback=1,                collide=COLLIDE_SOLID, toptex=1,  lefttex=1,  righttex=1,  fronttex=1,  backtex=1,  bottomtex=1,  sound=SOUND_STONE,  block_draw=BLOCK_DRAW_SOLID)
grass_block   = BlockType(block_id=2, name="Grass",       min_rank=constants.RANK_GUEST,    fallback=2,                collide=COLLIDE_SOLID, toptex=2,  lefttex=3,  righttex=3,  fronttex=3,  backtex=3,  bottomtex=2,  sound=SOUND_GRASS,  block_draw=BLOCK_DRAW_SOLID)
dirt_block    = BlockType(block_id=3, name="Dirt",        min_rank=constants.RANK_GUEST,    fallback=3,                collide=COLLIDE_SOLID, toptex=2,  lefttex=2,  righttex=2,  fronttex=2,  backtex=2,  bottomtex=2,  sound=SOUND_GRAVEL, block_draw=BLOCK_DRAW_SOLID)
cobble_block  = BlockType(block_id=4, name="Cobblestone", min_rank=constants.RANK_GUEST,    fallback=4,                collide=COLLIDE_SOLID, toptex=16, lefttex=16, righttex=16, fronttex=16, backtex=16, bottomtex=16, sound=SOUND_STONE,  block_draw=BLOCK_DRAW_SOLID)
wood_block    = BlockType(block_id=5, name="Wood",        min_rank=constants.RANK_GUEST,    fallback=5,                collide=COLLIDE_SOLID, toptex=4,  lefttex=4,  righttex=4,  fronttex=4,  backtex=4,  bottomtex=4,  sound=SOUND_WOOD,   block_draw=BLOCK_DRAW_SOLID)
sapling_block = BlockType(block_id=6, name="Sapling",     min_rank=constants.RANK_GUEST,    fallback=6, is_cube=False, collide=COLLIDE_AIR,                                       fronttex=15,                           sound=SOUND_GRASS,  block_draw=BLOCK_DRAW_SOLID)
bedrock_block = BlockType(block_id=7, name="Bedrock",     min_rank=constants.RANK_OPERATOR, fallback=7,                collide=COLLIDE_SOLID, toptex=17, lefttex=17, righttex=17, fronttex=17, backtex=17, bottomtex=17, sound=SOUND_STONE,  block_draw=BLOCK_DRAW_SOLID)

blocks = {
    0: air_block,
    1: stone_block,
    2: grass_block,
    3: dirt_block,
    4: cobble_block,
    5: wood_block,
    6: sapling_block,
    7: bedrock_block,
}

block_id_type = int