#!/usr/bin/env python3

# parse arguments
# accepted values are: 
# all, south, north, 
# fiber number (0 to 25)
# returns a dictionary of all selected crates, slots and channels

def parse_arguments( arguments ):

  # define fibers
  fibers_south = {5,  7,  6,  8,  9, 10, 24, 25}
  fibers_north = {11, 12, 18, 19, 0, 1,  14, 15}
  fibers_all = fibers_south|fibers_north

  # map fiber id to crate, slots and channels
  fiber_map = {
    # south side fibers
    5: {'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':4 },
    7: {'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':4 },
    6: {'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':7 },
    8: {'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':7 },
    9: {'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':6 },
    10:{'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':6 },
    24:{'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':8 },
    25:{'crate':'3A4-2', 'digital_slots':{15,16}, 'analog_slots':{14}, 'channel':8 },

    # north side fibers
    11:{'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':4 },
    12:{'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':4 },
    18:{'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':7 },
    19:{'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':7 },
    0: {'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':6 },
    1: {'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':6 },
    14:{'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':8 },
    15:{'crate':'3C4-2', 'digital_slots':{14,15}, 'analog_slots':{13}, 'channel':8 }
  }

  # get selected fiber list
  fibers = set()
  for arg in arguments:
    if arg == 'south' :
      fibers.update(fibers_south)
    elif arg == 'north':
      fibers.update(fibers_north)
    elif arg == 'all':
      fibers.update(fibers_all)
    elif arg.isdigit() and int(arg) in fibers_all:
      fibers.add( int(arg) )
    else: 
      print( f'unknown argument: {arg}' )

  channel_dict = dict()

  # create dictionary
  for fiber in fibers:

    # get channel definition
    channel_def = fiber_map[fiber]
    crate = channel_def['crate']

    if not crate in channel_dict.keys():
      channel_dict[crate] = dict()

    if not 'digital_slots' in channel_dict[crate].keys():
      channel_dict[crate]['digital_slots'] = set()
    channel_dict[crate]['digital_slots'] |= channel_def['digital_slots']

    if not 'analog_slots' in channel_dict[crate].keys():
      channel_dict[crate]['analog_slots'] = set()
    channel_dict[crate]['analog_slots'] |= channel_def['analog_slots']

    if not 'channels' in channel_dict[crate].keys():
      channel_dict[crate]['channels'] = set()
    channel_dict[crate]['channels'].add(channel_def['channel'])

  return channel_dict
