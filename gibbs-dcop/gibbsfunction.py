'''
    - Defines the functions specific to the SD-Gibbs algorithm
    - Assumes that the pseudotree is created and the agents are initialized
    - we let Z = 1
'''

import utils
import pickle
import socket
import agent
import numpy as np
import pseudotree_creation
#from simulation2 import allAgents

''' The following are helper functions '''

# function to sample from Eq. 21, i.e., SD-Gibbs sampling
def mapSample(agent):
    localMax = -10000   # temp variable to select max value
    arg = 0     # sampled value
    # iterate over domain to find argmax
    for d in agent.domain:
        utilitySum = 0
        for key1 in agent.context:
            d_j = agent.context[key1]
            utilitySum = utilitySum + agent.relations[(agent.id, key1)](d, d_j)
        prob = np.exp(utilitySum)
        if prob >= localMax:
            localMax = prob
            arg = d
    return arg

# function to find best utility so far
def argmaxValue(agent):
    localMax = -10000   # temp variable to select max value
    arg = 0     # sampled value
    # iterate over domain to find argmax
    for d in agent.domain:
        utilitySum = 0
        for key1 in agent.contextBar:
            d_j = agent.contextBar[key1]
            utilitySum = utilitySum + agent.relations[(agent.id, key1)](d, d_j)
        if utilitySum >= localMax:
            localMax = utilitySum
            arg = d
    return arg

# function to get delta, i.e., difference in utility
def getDelta(agent, currContext, type):
    localDelta = 0
    if type == 0:
        d = agent.d   # use d_i
    else:
        d = agent.dBar  # use d_i{BAR}

    for key in currContext:
        d_j = currContext[key]
        localDelta = localDelta + (agent.relations[(agent.id, key)](d, d_j) - agent.relations[(agent.id, key)](agent.dHat, d_j))
    return localDelta

''' The following are SD-Gibbs procedures '''

# sample() function: takes agent calling the function as parameter
def sample(agent):
    # the following piece of code are lines
    # 11 to 17 of Procedure SAMPLE() from the paper
    agent.t = agent.t + 1
    agent.dHat = agent.d
    agent.d = mapSample(agent)      # sampling from Eq. 21 of the paper
    agent.dBar = argmaxValue(agent) # keeping the best value
    agent.Delta = getDelta(agent, agent.context, 0)
    agent.DeltaBar = getDelta(agent, agent.contextBar, 1)
    ## we will send these values to all neighbors
    dataSend = [agent.id, agent.d, agent.dBar, agent.tStar, agent.tBar]
    for key in agent.c:
        agent.udp_send_VALUE("VALUE", dataSend, key)

# VALUE() function from SD-Gibbs paper
def VALUE(agent, id_s, d_s, dBar_s, tStar_s, tBar_s):
    # the following piece of code are lines
    # 18 to 36, i.e., Procedure VALUE() from the paper

    agent.context[id_s] = d_s
    if id_s in agent.pp or id_s == agent.p:
        agent.contextBar[id_s] = dBar_s
    else:
        agent.contextBar[id_s] = d_s

    if id_s == agent.p:
        if tBar_s >= tStar_s and tBar_s > max(agent.tStar, agent.tBar):
            agent.dStar = agent.dBar
            agent.tBar = tBar_s
        elif tStar_s >= tBar_s and tStar_s > max(agent.tStar, agent.tBar):
            agent.dStar = agent.d
            agent.tStar = tStar_s
        sample(agent)

        if agent.c == []:
            sendData = [agent.id, agent.Delta, agent.DeltaBar]
            agent.udp_send_BACKTRACK("BACKTRACK", sendData, id_s)

# BACKTRACK() function from SD-Gibbs paper
def BACKTRACK(agent, id_s, Delta_s, DeltaBar_s):
    agent.Delta = agent.Delta + Delta_s
    agent.DeltaBar = agent.DeltaBar + DeltaBar_s
    agent.childBack.append(id_s)
    print agent.childBack, agent.c
    if len(agent.childBack) == len(agent.c):
        agent.childBack = []
        if agent.is_root == False:
            sendData = [agent.id, agent.Delta, agent.DeltaBar]
            agent.udp_send_BACKTRACK("BACKTRACK", sendData,agent.p)
        if agent.is_root == True:
            agent.deltaBar = agent.delta + agent.DeltaBar
            agent.delta = agent.delta + agent.Delta
            if agent.delta >= agent.deltaBar and agent.delta > agent.deltaStar:
                agent.deltaStar = agent.delta
                agent.dStar = agent.d
                agent.tStar = agent.t
            elif agent.deltaBar >= agent.delta and agent.deltaBar > agent.delta:
                agent.deltaStar = agent.deltaBar
                agent.dStar = agent.dBar
                agent.tStar = agent.t
            print "This iteration's value : " + str(agent.deltaStar)
            ## this is a new iteration
            sample(agent)
