"""
This module handles the initial part of the algorithm, which is the pseudo-tree
creation.
"""

import threading
import socket
import time
import gibbsfunction
import utils
import pseudotree
import agent
import graphs
import thread

Relatives = utils.Relatives





def gibbs_listerner_creation_value(agent):

    # Wait till the message VALUE(agent, id_s, d_s, dBar_s, tStar_s, tBar_s) [has title: 'VALUE'] arrives
    # from some agent.
    while ('VALUE' not in agent.msgs) & ('BACKTRACK' not in agent.msgs):
        #print agent.id
        pass
    # do the gibbs function
    try:
        thread.start_new_thread( gibbs_listerner_creation_value, (agent) )
    except:
        print "Error! Cant open listener"
        
    assign_values(agent)

def assign_values(agent):

    if 'VALUE' in agent.msgs:
        # unpack the received values
        id_s, d_s, dBar_s, tStar_s, tBar_s = agent.msgs['VALUE']
        # once agent gets VALUE msg it updates its value
        gibbsfunction.VALUE(agent, id_s, d_s, dBar_s, tStar_s, tBar_s)
        # delete key to receive new
        del agent.msgs['VALUE']

    else:
        # unpack the receiveed values
        id_s, Delta_s, DeltaBar_s = agent.msgs['BACKTRACK']
        # call the gibbs BACKTRACK function
        gibbsfunction.BACKTRACK(agent, id_s, Delta_s, DeltaBar_s)
        # delete key to receive new
        del agent.msgs['BACKTRACK']

    if agent.is_root:
        print "Current Utility: " + str(agent.deltaStar)

    # start listening again
    gibbs_listerner_creation_value(agent)
