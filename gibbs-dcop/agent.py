"Defines the class Agent which represents a node/agent in the DPOP algorithm."

import utils
import pickle
import socket
import gibbsfunction
import pseudotree_creation
import time
import os
import gibbs_listener
#import utilmsgprop
#import valuemsgprop

## dict of all agents
allAgents = {}
## dict of all processes
pid = 0
children = {}


class Agent:
    def __init__(self, i, domain, relations, agents_file):
        # Use utils.get_agents_info to initialize all the agents.
        # All the information from 'agents.txt' will be retrieved and stored in
        # this dict 'agents_info'.
        # Also, the domains of some agents will be added to this dict later on.
        # You can access a value as:
        # agent.agents_info[<agent_id>]['field_required']
        # Some miscellaneous information will be stored with id=42.

        self.agents_info = utils.get_agents_info(agents_file)
        info = self.agents_info
        self.processID = None

        self.value = -1  # The value that will be selected for this agent
        self.max_util = float("-inf")  # Will be initialized only for the root, in the end
        self.i = self.id = i
        allAgents[i] = self   # agent added to overall list
        self.domain = domain  # A list of values
        self.relations = relations  # A dict of functions, for each edge in the
                                    # graph
        self.graph_nodes = self.get_graph_nodes()  # A list of all the nodes in
                                                   # the graph, except itself
        self.neighbors = self.get_neighbors()  # A list of all the neighbors
                                               # sorted by ids
        self.p = None  # The parent's id
        self.pp = []  # A list of the pseudo-parents' ids
        self.c = []  # A list of the childrens' ids
        self.pc = None # A list of the pseudo-childrens' ids
        self.table =  None  # The table that will be stored
        self.table_ant = None  # The ANT of the table that will be stored
        self.IP = info[self.id]['IP']
        self.PORT = eval(info[self.id]['PORT'])  # Listening Port

        ''' agent values for gibbs DCOP
            These lines act as the Initialize() function of SD-Gibbs
        '''

        self.d = 0 # agent's value in the current iteration
        self.dHat = 0 # agent's value in the previous iteration
        self.dStar = 0 # agent's value in the best complete solution so far
        self.context = {} # agent's context : tuple of all neighbors and their values
        self.dBar = 0 # agent's value that maximizes its local solution under the context
        self.contextBar = {} # agent's current best response context
        self.t = 0 # number of iteration the agent has sampled
        self.tStar = 0 # iteration where best non-best-response is found
        self.tBar = 0 # iteration where best best-response is found
        self.Delta = 0 # difference in solution quality of current iteration with previous
        self.DeltaBar = 0 # difference in solution quality of best response iteration with current

        ''' Initialize() ends '''

        self.childBack = [] # list to keep track of all messages received from children per iteration

        self.is_root = False
        if 'is_root' in info[self.i]:
            self.is_root = eval(info[self.i]['is_root'])
            # if agent is root, in Gibbs it has the following additional values
            self.delta = 0
            self.deltaBar = 0
            self.deltaStar = 0

        self.root_id = eval(info[42]['root_id'])
        self.msgs = {}  # The dict where all the received messages are stored
                        # Key VALUE: where all the VALUE messages are received

        # code for debugging utility function
        #for key in self.relations:
            #print key
            #print self.relations[key](0,0)

        # initializing context
        for x in self.get_neighbors():
            self.context[x] = 0
            self.contextBar[x] = 0

        # the root agent in Gibbs starts the sampling
        #if self.is_root == True:
            #time.sleep(10)
            #gibbsfunction.sample(self)        # call the sample


    def get_graph_nodes(self):
        info = self.agents_info
        graph_nodes = []
        for key in info:
            if key != 42 and key != self.id:
                graph_nodes.append(key)
        return graph_nodes

    def get_neighbors(self):
        L = []
        for first, second in self.relations.keys():
            L.append(second)
        return sorted(L)

    def calculate_util(self, tup, xi):
        """
        Calculates the util; given a tuple 'tup' which has the assignments of
        values of parent and pseudo-parent nodes, in order; given a value 'xi'
        of this agent.
        """
        # Assumed that utilities are combined by adding to each other
        util = self.relations[self.id, self.p](xi, tup[0])
        for index, x in enumerate(tup[1:]):
            util = util + self.relations[self.id, self.pp[index]](xi, x)
        return util

    def is_leaf(self):
        "Return True if this node is a leaf node and False otherwise."

        assert self.c != None, 'self.c not yet initialized.'
        if self.c == []:
            return True
        else:
            return False

    def udp_send(self, title, data, dest_node_id):
        """
        Send a UDP message to the node whose id is given by 'dest_node_id'; the
        'title' is the message's title string and 'data' is the content object.
        """
        print str(self.id) + ': udp_send, sending a message ...'

        info = self.agents_info
        pdata = pickle.dumps((title, data))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pdata, (info[dest_node_id]['IP'], int(info[dest_node_id]['PORT'])))
        sock.close()

        print str(self.id) + ': Message sent, ' + title + ": " + str(data)


    def udp_send_VALUE(self, title, data, dest_node_id):
        """
        Send a UDP message to the node whose id is given by 'dest_node_id'; the
        'title' is the message's title string and 'data' is the content object.
        This is the VALUE() message in SD-Gibbs
        """
        print str(self.id) + ': udp_send, sending a message ...'

        info = self.agents_info
        pdata = pickle.dumps((title, data))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pdata, (info[dest_node_id]['IP'], int(info[dest_node_id]['PORT'])))
        sock.close()

        ''' update the value in the destination agent's context
        if self.processID == dest_node_id:
            gibbsfunction.VALUE(self, self.id, self.d, self.dBar, self.tStar, self.tBar)
        '''

        print str(self.id) + ': Message sent, ' + title + ": " + str(data)

    def udp_send_BACKTRACK(self, title, data, dest_node_id):
        """
        Send a UDP message to the node whose id is given by 'dest_node_id'; the
        'title' is the message's title string and 'data' is the content object.
        This is the VALUE() message in SD-Gibbs
        """
        print str(self.id) + ': udp_send, sending a message ...'

        info = self.agents_info
        pdata = pickle.dumps((title, data))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pdata, (info[dest_node_id]['IP'], int(info[dest_node_id]['PORT'])))
        sock.close()

        ''' update the value in the destination agent's context
        gibbsfunction.BACKTRACK(allAgents[dest_node_id], self.id, self.Delta, self.DeltaBar)
        '''

        print str(self.id) + ': Message sent, ' + title + ": " + str(data)

    def start(self):
        print str(self.id)+': Started'
        pseudotree_creation.pseudotree_creation(self)
        #print self.pp, self.p
        #utilmsgprop.util_msg_prop(self)
        if self.is_root==True:
            #print 'hi i am root'
            gibbsfunction.sample(self)        # call the sample
            #valuemsgprop.value_msg_prop(self)
        gibbs_listener.gibbs_listerner_creation_value(self)
        print str(self.id)+': Finished'

    def start_gibbs(self):
        gibbsfunction.sample(self)        # call the sample


def _test():
    from pprint import pprint, pformat

    # A relation that takes two variables' values as inputs
    def f(xi, xj):
        return x+y

    agent1 = Agent(1, [7, 1, 4, 5], {(1,2): f, (1,4): f, (1,3): f})
    pprint(vars(agent1))


if __name__ == '__main__':
    _test()
