mcmaketest
==========

:Description: Test world generator for minecraft.
:Author:      Xgkkp

Asks various questions about the world specification, and then generates
a fresh, flat stone minecraft world with user defined hollow layers, whose size
and spacing is also user-defined. Each chunk is marked with cobblestone, and a
pymclevel "Creative in a box" schematic is created at the spawn location, in
addition to basic tools in the players inventory.

If you specify hollow layers, glass ceiling windows are created for automatic
daylight lighting.

There is currently a bug whereby saving and reloading inside minecraft causes
the player data to be lost (but the world the same).

.. image:: minecraft_testlevel.jpg

Usage
-----
Simply use python to run the script, in the form::

  $ python maketest.py {name_of_new_world}

And a new folder will be created with the specified name. You can then copy this
across to the minecraft save folder. Here is an example run::

  $ python maketest.py test_world
  Number of Hollow Layers? [0] 2
  Layer block thickness? [0] 1
  Air height of Layers? [0] 3
  Generating chunks with:
    - 2 hollow layers
    - of 1 thickness
    - with 3 headroom
  Making test world named test_world
    in /home/user/mcmaketest/test_world
  Generating Lights
  $

Requirements
------------

pymclevel_ 
      For most of the heavy lifting; object-based access
      to chunk creation and alteration, and especially the lighting
      
NBT_:       
      Because I haven't yet changed the script to use the pymclevel nbt reader, which
      seems a little more simplistic

.. _pymclevel: https://github.com/codewarrior0/pymclevel
.. _NBT: https://github.com/twoolie/NBT

Known Bugs
----------

- For some reason, the world loads inside minecraft fine, but when you save and reload all
  the player data is lost. I assume this is some weird behaviour because I have set up the player structure
  incorrectly, but have been unable to diagnose it as of yet.
- I get a deprecation warning in the NBT module at the moment, though my copy may be out of date
