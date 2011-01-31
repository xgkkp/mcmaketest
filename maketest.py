#!/usr/bin/env python

"""Test world generator.

Asks various questions about the world specification, and then generates
a fresh, flat stone minecraft world with user defined hollow layers, whose size
and spacing is also user-defined. Each chunk is marked with cobblestone, and a
pymclevel "Creative in a box" schematic is created at the spawn location, in
addition to basic tools in the players inventory.

If you specify hollow layers, glass ceiling windows are created for automatic
daylight lighting.

There is currently a bug whereby saving and reloading inside minecraft causes
the player data to be lost (but the world the same).

Reqires:
  pymclevel: https://github.com/codewarrior0/pymclevel
  NBT:       https://github.com/twoolie/NBT
       (because I haven't yet changed it to use the pymclevel nbt reader, which
        is a little more simplistic)
"""

from pymclevel import mclevel
import nbt
import base64

from gzip import GzipFile

import sys, os

import time
from optparse import OptionParser


def get_int(question, default=0):
  print question + "?",
  #if default != 0:
  print "[{default}]".format(default=default),
  inval = raw_input()
  try:
    return int(inval)
  except:
    return default

def PlayerTag():
  player = nbt.TAG_Compound()
  player.name = "Player"
  # Rest of the player data
  position = nbt.TAG_List(name="Pos", type=nbt.TAG_Double)
  position.tags.extend([nbt.TAG_Double(0.5), nbt.TAG_Double(options.groundheight+2), nbt.TAG_Double(0.5)])
  player.tags.append(position)
  motion = nbt.TAG_List(name="Motion", type=nbt.TAG_Double)
  motion.tags.extend([nbt.TAG_Double(0.), nbt.TAG_Double(0.), nbt.TAG_Double(0.)])
  player.tags.append(motion)
  rotation = nbt.TAG_List(name="Rotation", type=nbt.TAG_Float)
  rotation.tags.extend([nbt.TAG_Float(0.), nbt.TAG_Float(0.)])
  player.tags.append(rotation)

  player.tags.append(nbt.TAG_Byte(name="OnGround", value=1))
  player.tags.append(nbt.TAG_Short(name="Air", value=300))
  player.tags.append(nbt.TAG_Short(name="HurtTime", value=0))
  player.tags.append(nbt.TAG_Short(name="AttackTime", value=0))
  player.tags.append(nbt.TAG_Short(name="DeathTime", value=0))
  player.tags.append(nbt.TAG_Short(name="Health", value=20))
  player.tags.append(nbt.TAG_Short(name="Fire", value=-20))
  player.tags.append(nbt.TAG_Int(name="Score", value=0))
  player.tags.append(nbt.TAG_Long(name="Dimension", value=0))

  player.tags.append(nbt.TAG_Float(name="FallDistance", value=0.0))

  inventory = nbt.TAG_List(name="Inventory", type=nbt.TAG_Compound)
  inventory.tags.append(Itemstack(278, slot=8))
  inventory.tags.append(Itemstack(50, slot=0, count=-1)) # Torches
  inventory.tags.append(Itemstack(1, slot=1, count=-1))  # Stone
  inventory.tags.append(Itemstack(3, slot=2, count=-1))  # Dirt
  inventory.tags.append(Itemstack(345, slot=35, count=1))  # Compass



  player.tags.append(inventory)

  return player

def Itemstack(item, slot, count=1):
  stack = nbt.TAG_Compound()
  stack.name = ''
  stack.tags.append(nbt.TAG_Short(name="id", value=item))
  stack.tags.append(nbt.TAG_Byte(name="Slot", value=slot))
  stack.tags.append(nbt.TAG_Byte(name="Count", value=count))
  stack.tags.append(nbt.TAG_Short(name="Damage", value=0))
  return stack

def Create_LevelDat(filename):
  "Creates a blank level.dat suitable for initializing fresh worlds"
  # Make a blank NBT
  level = nbt.NBTFile()
  level.name = ''
  # data compound
  data = nbt.TAG_Compound()
  data.name = "Data"
  data.tags.append(nbt.TAG_Int(name="SpawnX", value=0))
  data.tags.append(nbt.TAG_Int(name="SpawnY", value=64))
  data.tags.append(nbt.TAG_Int(name="SpawnZ", value=0))
  data.tags.append(nbt.TAG_Long(name="LastPlayed", value=time.time()))
  data.tags.append(nbt.TAG_Long(name="RandomSeed", value=42))
  data.tags.append(nbt.TAG_Long(name="SizeOnDisk", value=0))
  data.tags.append(nbt.TAG_Long(name="Time", value=0))

  data.tags.append(PlayerTag())

  level.tags.append(data)
  level.write_file(filename)


def FillChunk(chunk):
  """Creates the block data for a new chunk, based on program options"""
  H = options.groundheight
  # Lots of Stone
  chunk.Blocks[:,:,:H] = 1

  layerstep = options.headroom+options.thickness
  if layerstep == 0:
    layerstep = 1

  # Make glass columns
  minglass = H - (options.layers) * layerstep
  chunk.Blocks[5,5,minglass:H] = 20
  chunk.Blocks[11,5,minglass:H] = 20
  chunk.Blocks[5,11,minglass:H] = 20
  chunk.Blocks[11,11,minglass:H] = 20

  # Make the voids in the layers  
  for i in range(H-layerstep, 1, -layerstep)[:options.layers]:
    # Hollow out the air from here upwards
    chunk.Blocks[:,:,i:i+options.headroom] = 0

  # Make 'direction' columns of cobblestone at the chunk corners
  # chunk.Blocks[0:2,0,:H] = 4
  # chunk.Blocks[0,0:2,:H] = 4
  chunk.Blocks[:,0,:H] = 4
  chunk.Blocks[0,:,:H] = 4

  # Make the bottom level bedrock
  chunk.Blocks[:,:,0] =  7
  # This flag looks like it should control the existence of ore, trees, etc,
  # but doesn't actually seem to do anything (It looks like anything next to a
  # freshly generated chunk is automatically populated with such things)
  # chunk.TerrainPopulated = 1
  # chunk.root_tag["Level"]["LastUpdate"].value = 1
  chunk.chunkChanged()
  
if __name__ == '__main__':
  # Set up the options parser and parse the arguments
  usagestr = "usage: %prog {name}"
  parser = OptionParser(usage=usagestr)
  # parser.add_option("-s", "--size", dest="host", metavar="SIZE", default=3,
  #                   help="")
  (options, args) = parser.parse_args()

  options.groundheight = 64
  options.layers = get_int("Number of Hollow Layers")
  options.thickness = get_int("Layer block thickness")
  options.headroom = get_int("Air height of Layers")

  print """Generating chunks with:
  - {layers} hollow layers
  - of {thickness} thickness
  - with {air} headroom""".format(layers=options.layers, thickness=options.thickness,air=options.headroom)

  if not len(args):
    print "Must specify a name for the new level!"
    sys.exit(1)

  worldpath = os.path.abspath(args[0])
  worldname = os.path.basename(worldpath)
  worldleveldat = os.path.join(worldpath, "level.dat")

  print "Making test world named", worldname
  print "  in", worldpath

  if os.path.exists(worldpath):
    print "Error: Path already exists"
    sys.exit(1)

  # Create the world folder and level.dat
  os.makedirs(worldpath)
  
  Create_LevelDat(worldleveldat)

  # Open the world
  world = mclevel.fromFile(worldpath)

  # Now, we can get to the business of creating
  chunkrad = 5
  for x in range(-chunkrad, chunkrad):
    for z in range(-chunkrad, chunkrad):
      world.createChunk(x,z)
      chunk = world.getChunk(x,z)
      FillChunk(chunk)
  # chunk.chunkChanged()

  # Place a 'creative' box
  destPoint = (-3,options.groundheight,0)
  boxschem = mclevel.fromFile("CreativeInABox.schematic")
  world.copyBlocksFrom(boxschem, boxschem.bounds, destPoint);

  print "Generating Lights"
  world.generateLights()
  world.saveInPlace()
