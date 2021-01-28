import MySQLdb
import numpy as np
from tarjan import tarjan # The Tarjan algorithm is employed to find the GSCC, the code can be downloaded from https://github.com/bwesterb/py-tarjan.

MAX_ID = 99546027 # Size of original network.
Subnet_Size = 300000 # The data-driven site percolation constructs a sub-network. Subnet_Size is the subnetwork size.
Add_node = 1000 #  Executing the percolation, beta is increased gradually by <#Add_node> nodes that are added into the subnetwork.

# This program firstly construct a sub-network with <#Subnet_Size> nodes, and reset the node Id in the sub-network.
# Then secondly obtain the results on subsub-network with different beta based on this sub-network.

def whole_simulation():
    conn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='******', db='weibo_100m')
        # Please fill in the passwd, and the input of the function may be altered based on your database connection.
    cur = conn.cursor()

    # Pick <#Subnet_Size> nodes.
    # Id_100M is the node Id in original network, from 1 to MAX_ID; Id_Sub is the node Id in the sub-netwokr of the picked nodes, from 0 to NumNodeChosen - 1.
    node_List = picking_nodes() # The list of picked nodes.
    node_100M2Sub = {}  # The inversion of nodeList, i.e., node_100M2Sub[Id_100M] = Id_Sub <==> node_List[Id_Sub] = Id_100M.
    # node_100M2Sub is used when constructing the sub-network.
    for Id_Sub in range(Subnet_Size):
        Id_100M = node_List[Id_Sub]
        node_100M2Sub[Id_100M] = Id_Sub
    pickedSet = set(node_List)  # The set of picked nodes, which is used to judge whether the node has been picked.
    print 'Pick nodes over'

    # Construct sub-network of <#subnet_Size> nodes.
    graphDict = {}  # The sub-network constructed by data-driven site percolation is recorded by graphDict.
    # graphDict[Id_Sub] records the intersection between <#pickedSet> and the follower of node node_100M2Sub[Id_Sub].
    for Id_Sub in range(Subnet_Size):
        Id_100M = node_List[Id_Sub] # Handling this user.
        sql_cmd = "select fans from fan_table where id = %d" % (Id_100M)
        cur.execute(sql_cmd)
        results = cur.fetchall()
        results = results[0][0]
        edges = []
        if results != '[]':
            followers = results.split(',')
            k_out = len(followers)
            followers[0] = followers[0].strip('[')
            followers[k_out-1] = followers[k_out-1].strip(']')
            for k_now in range(k_out):
                follower_now = eval(followers[k_now])
                if follower_now in pickedSet:
                    edges.append(node_100M2Sub[follower_now])  # The follower list of the retweeting user.
        graphDict[Id_Sub] = edges
    print 'Construct sub-network over'

    # Find GSCC and GOUT of subsub-networks: increasing the subsub-network size in range(Add_node, Subnet_Size+Add_node, Add_node).
    # In the code below, the users' Id in the original network (with 100 million nodes) are not used.
    subGraphDict = {}
    preBoard = 0
    nowBoard = Add_node
    while nowBoard <= Subnet_Size:
        # Construct the subsub-network with <#newBoard> nodes based on the subsub-network with <#preBoard> nodes.
        for Id_Sub in range(preBoard): # New edges: Ids in range(preBoard) --> Ids in range(preBoard, nowBoard).
            for follower in graphDict[Id_Sub]:
                if follower < nowBoard and follower >= preBoard:
                    subGraphDict[Id_Sub].append(follower)
        for Id_Sub in range(preBoard, nowBoard): # New edges: Ids in range(preBoard, nowBoard) --> Ids in range(nowBoard).
            edges = []
            for follower in graphDict[Id_Sub]:
                if follower < nowBoard:
                    edges.append(follower)
            subGraphDict[Id_Sub] = edges

        # Find GSCC.
        sccList = tarjan(subGraphDict) # Find strongly connected components (SCCs).
        gscc_id = -1
        gscc_Size = 0
        for sccId in range(len(sccList)):
            size = len(sccList[sccId])
            if size > gscc_Size:
                gscc_id = sccId
                gscc_Size = size

        # Find GOUT by BFS from one node in GSCC.
        source = sccList[gscc_id][0] # The GOUT is equivalent to the out-component of any node in the GSCC.
        nodesTobeVisited = set()
        reachOrNot = np.array([False] * nowBoard ) # Whether each node belongs to the GOUT.
        reachOrNot[source] = True
        nodesTobeVisited.add(source)
        while len(nodesTobeVisited) > 0:
            nodeVisiting = nodesTobeVisited.pop()
            for follower in subGraphDict[nodeVisiting]:
                if reachOrNot[follower] == False:
                    nodesTobeVisited.add(follower)
                    reachOrNot[follower] = True
        goutSize = sum(reachOrNot)

        beta = 1.0*nowBoard/MAX_ID # Proportion of picked nodes.
        goutSize_norm = 1.0*goutSize/MAX_ID # Normalized cascade size.
        print beta, goutSize_norm
        preBoard += Add_node
        nowBoard += Add_node

def kout2activity(kout):
    if kout < 4.41e6:
        p_kout = 0.087 * pow(kout,0.284)
        return p_kout
    else:
        p_kout = 6.5e4 * pow(kout,-0.6)
        return p_kout

def picking_nodes():
    p_pick = np.array([0.0] * (MAX_ID + 1))
    in_file = open('k_each_user.txt','r')
    for each_line in in_file:
        each_line = each_line.strip()
        values = each_line.split('\t')
        node_id = eval(values[0])
        kout = eval(values[2])
        p_pick[node_id] = kout2activity(kout)
    p_pick[0] = 0.0 # Node 0 is not exist in the original network.
    norm_const = sum(p_pick)
    for node_id in range(MAX_ID + 1):
        p_pick[node_id] = p_pick[node_id] / norm_const
    in_file.close()
    print 'Calculation of the probability to picked over.'
    return  np.random.choice(MAX_ID + 1, Subnet_Size, replace=False, p=p_pick)

if __name__ == "__main__":
    whole_simulation()
