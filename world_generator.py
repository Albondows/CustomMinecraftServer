import random
import math

import block
import world

def empty_world_generator(width: int, height: int, length: int, seed: int) -> list[block.Block()]:
    return [block.AirBlock()] * width * height * length

def flat_world_generator(width: int, height: int, length: int, seed: int) -> list[block.Block()]:
    return ([block.BedrockBlock()] * width * length) + ([block.DirtBlock()] * width * (height // 2 - 2) * length) + ([block.GrassBlock()] * width * length) + ([block.AirBlock()] * width * (height // 2) * length)

