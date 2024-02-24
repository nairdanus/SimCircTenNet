import numpy as np
import tensornetwork as tn
from parseQCP import *
from simulator import *
import os
from helpers import *
import sys

def plot(sim):
    #import networkx as nx
    #import matplotlib.pyplot as plt
    
    print("https://dreampuf.github.io/GraphvizOnline/", file=sys.stderr)
    #
    for x in sim.network:
        x.name = str(x.tensor.shape)
        y: tn.Node = x
        #y.set_tensor
        for i, e in enumerate(y.edges):
            new_name = str(e.dimension)
            if e.name != "" and e.name != "__unnamed_edge__":
                assert e.name == new_name, e.name + ' != ' + new_name
            e.name = new_name
            
    gv = tn.to_graphviz(sim.network)
    print(gv)
    
    """
    g = nx.DiGraph()
    g.add_node(" ajdkaj skldas")
    g.add_node("huhn")

    pos = nx.spring_layout(g)
    #nx.draw_networkx_labels(g, pos)
    
    nx.draw_networkx(g,
                #pos = {0:(0, 0), 1: (1, 0)},
                node_size = 0,
                 arrows = True,
                #labels = {0:"Python",1:"Programming"},
                 bbox = dict(facecolor = "skyblue")
                )
    #nx.draw_networkx_nodes(g, pos)
    #nx.draw_networkx_labels(G, pos)
    #nx.draw_networkx_edges(G, pos, edge_color='r', arrows = True)
    plt.show()
    """
    """
    G = nx.DiGraph()
    G.add_node("A")
    G.add_node("B")
    G.add_node("C")
    G.add_node("D")
    G.add_node("E")
    G.add_node("F")
    G.add_node("G")
    G.add_edge("A","B")
    G.add_edge("B","C")
    G.add_edge("C","E")
    G.add_edge("C","F")
    G.add_edge("D","E")
    G.add_edge("F","G")
    

    print(G.nodes())
    print(G.edges())

    pos = nx.spring_layout(G)

    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edge_color='r', arrows = True)

    plt.show()
    """
    #"""
    """
    import matplotlib.pyplot as plt 
    
    # x axis values 
    x = [1,2,3] 
    # corresponding y axis values 
    y = [2,4,1] 
    
    # plotting the points  
    plt.plot(x, y) 
    
    # naming the x axis 
    plt.xlabel('x - axis') 
    # naming the y axis 
    plt.ylabel('y - axis') 
    
    # giving a title to my graph 
    plt.title('My first graph!') 
    
    # function to show the plot 
    plt.show() 
    """


if __name__ == "__main__":    
    assert len(sys.argv) == 2
    path = sys.argv[1]
    assert os.path.isfile(path)
    assert path.endswith(".qcp")

    c = parseQCP(path)
    simulator = MPS_Simulator(c)
    simulator.iterate_circ()

    plot(simulator)
    #exit(0)
    #result = simulator.get_result()
    #r = np.reshape(result.tensor, newshape=(2**simulator.circ.numQubits))

    #print(r)
    #print(v2s(r))