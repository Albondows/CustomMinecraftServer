class Block:
    block_id = 0
    name     = "" 

    def __init__(self):
        pass

    def __int__(self):
        return self.block_id

    def to_bytes(self):
        return self.block_id.to_bytes(2, byteorder="big")

class AirBlock(Block):
    block_id = 0
    name     = "Air"
    
    def __init__(self):
        pass

    def __int__(self):
        return self.block_id
    
    def to_bytes(self):
        return self.block_id.to_bytes(2, byteorder="big")

class StoneBlock(Block):
	block_id = 1
	name     = "Stone"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class GrassBlock(Block):
	block_id = 2
	name     = "Grass Block"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class DirtBlock(Block):
	block_id = 3
	name     = "Dirt"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class CobblestoneBlock(Block):
	block_id = 4
	name     = "Cobblestone"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class PlanksBlock(Block):
	block_id = 5
	name     = "Planks"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class SaplingBlock(Block):
	block_id = 6
	name     = "Sapling"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class BedrockBlock(Block):
	block_id = 7
	name     = "Bedrock"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class FlowingWaterBlock(Block):
	block_id = 8
	name     = "Flowing Water"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class StationaryWaterBlock(Block):
	block_id = 9
	name     = "Stationary Water"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class FlowingLavaBlock(Block):
	block_id = 10
	name     = "Flowing Lava"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class StationaryLavaBlock(Block):
	block_id = 11
	name     = "Stationary Lava"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class SandBlock(Block):
	block_id = 12
	name     = "Sand"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class GravelBlock(Block):
	block_id = 13
	name     = "Gravel"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class GoldOreBlock(Block):
	block_id = 14
	name     = "Gold Ore"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class IronOreBlock(Block):
	block_id = 15
	name     = "Iron Ore"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class CoalOreBlock(Block):
	block_id = 16
	name     = "Coal Ore"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class WoodBlock(Block):
	block_id = 17
	name     = "Wood"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class LeavesBlock(Block):
	block_id = 18
	name     = "Leaves"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class SpongeBlock(Block):
	block_id = 19
	name     = "Sponge"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

class GlassBlock(Block):
	block_id = 20
	name     = "Glass"

	def __init__(self):
		pass
	
	def __int__(self):
		return self.block_id

blocks = {
0:  AirBlock,
1:  StoneBlock,
2:  GrassBlock,
3:  DirtBlock,
4:  CobblestoneBlock,
5:  PlanksBlock,
6:  SaplingBlock,
7:  BedrockBlock,
8:  FlowingWaterBlock,
9:  StationaryWaterBlock,
10: FlowingLavaBlock,
11: StationaryLavaBlock,
12: SandBlock,
13: GravelBlock,
14: GoldOreBlock,
15: IronOreBlock,
16: CoalOreBlock,
17: WoodBlock,
18: LeavesBlock,
19: SpongeBlock,
20: GlassBlock,

}