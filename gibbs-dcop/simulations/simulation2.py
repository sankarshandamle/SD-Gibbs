# A simulation with negative values
# Simulation 2

# This module illustrates a simulation using negative util values.
# You can model a cost problem like this; just convert the (+ve) cost values to
# (-ve) utility values.

import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import agent


def f12(x1, x2):
    if (x1, x2) == (0, 0): return -1
    elif (x1, x2) == (0, 1): return 0
    elif (x1, x2) == (1, 0): return 0
    elif (x1, x2) == (1, 1): return 0
    else: raise ValueError

def f14(x1, x4):
    if (x1, x4) == (0, 0): return 0
    elif (x1, x4) == (0, 1): return 1
    elif (x1, x4) == (1, 0): return 0
    elif (x1, x4) == (1, 1): return 0
    else: raise ValueError

def f21(x2, x1):
    return f12(x1, x2)

def f13(x1, x3):
    if (x1, x3) == (0, 0): return -1
    elif (x1, x3) == (0, 1): return -2
    elif (x1, x3) == (1, 0): return -2
    elif (x1, x3) == (1, 1): return -1
    else: raise ValueError

def f31(x3, x1):
    return f13(x1, x3)

def f23(x2, x3):
    if (x2, x3) == (0, 0): return 0
    elif (x2, x3) == (0, 1): return 0
    elif (x2, x3) == (1, 0): return 1
    elif (x2, x3) == (1, 1): return 0
    else: raise ValueError

def f32(x3, x2):
    return f23(x2, x3)

def f24(x2, x4):
    if (x2, x4) == (0, 0): return 0
    elif (x2, x4) == (0, 1): return 0
    elif (x2, x4) == (1, 0): return 0
    elif (x2, x4) == (1, 1): return -2
    else: raise ValueError

def f42(x4, x2):
    return f24(x2, x4)

def f41(x4, x1):
    return f14(x1, x4)

agents_file = "agents-sim-2.txt"

agent1 = agent.Agent(1, [0, 1],
     {(1,2): f12,
      (1,4): f14},
      agents_file)

agent2 = agent.Agent(2, [0, 1],
    {(2,4): f24,
     (2,1): f21,
     (2,3): f23},
     agents_file)

agent3 = agent.Agent(3, [0, 1],
    {(3, 2): f32},
     agents_file)

agent4 = agent.Agent(4, [0, 1],
    {(4,2): f42,
      (4,1) : f41},
    agents_file)

#allAgents = [agent1, agent2, agent3, agent4]

# A trick so that this process is allowed to fork.

pid = os.getpid()
children = []

if pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        agent2.processID = 2
        agent2.start()
        print 'agent2:', agent2.value

if pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        agent3.processID = 3
        agent3.start()
        print 'agent3:', agent3.value

if pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        agent4.processID = 4
        agent4.start()
        print 'agent4:', agent4.value


if pid == os.getpid():
    agent1.processID = 1
    agent1.start()
    #agent1.start_gibbs()
    print 'max_util:', agent1.max_util
    print 'agent1:', agent1.value
    for i in children:
        os.wait()
