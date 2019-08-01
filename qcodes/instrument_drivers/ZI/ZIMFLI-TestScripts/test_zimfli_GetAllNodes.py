# -*- coding: utf-8 -*-
"""
File: test_zimfli_GetAllNodes.py
Date: Feb / Mar 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to list all available nodes of the instrument
"""

from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI


# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

nodes = []
# High-Speed nodes are never listed (e.g. demods/0/sample)
tmp = zidev._list_nodes("*")
#node_list = self.daq.getList('/{}/{}/'.format(self.device, node), 0 )

for t in tmp:
    nodes.append(t[0].lower())
#    print( t[0] )

print( len(nodes) )

#tmp = zidev.daq.listNodes( "/dev4039/*", 0x23 )
tmp = zidev.daq.listNodes( "*", 0x23 )
for t in tmp:
    if not t.lower() in nodes:
        print( t )
        nodes.append( t.lower() + " *" )

nodes.sort()

print( len(nodes) )
for n in nodes:
    print(n)

# |  listNodes(...)
# |      listNodes( (ziDAQServer)arg1, (str)arg2, (int)arg3) -> list :
# |          This function returns a list of node names found at the specified path.
# |              arg1: Reference to the ziDAQServer class.
# |              arg2: Path for which the nodes should be listed. The path may
# |                    contain wildcards so that the returned nodes do not
# |                    necessarily have to have the same parents.
# |              arg3: Enum that specifies how the selected nodes are listed.
# |                    ziPython.ziListEnum.none -> 0x00
# |                         The default flag, returning a simple
# |                         listing of the given node
# |                    ziPython.ziListEnum.recursive -> 0x01
# |                         Returns the nodes recursively
# |                    ziPython.ziListEnum.absolute -> 0x02
# |                         Returns absolute paths
# |                    ziPython.ziListEnum.leafsonly -> 0x04
# |                         Returns only nodes that are leafs,
# |                         which means the they are at the
# |                         outermost level of the tree.
# |                    ziPython.ziListEnum.settingsonly -> 0x08
# |                         Returns only nodes which are marked
# |                         as setting
# |                    ziPython.ziListEnum.streamingonly -> 0x10
# |                         Returns only streaming nodes
# |                    ziPython.ziListEnum.subscribedonly -> 0x20
# |                         Returns only subscribed nodes
# |                    ziPython.ziListEnum.basechannel -> 0x40
# |                         Return only one instance of a node in case of multiple
# |                         channels
# |                    Or any combination of flags can be used.
