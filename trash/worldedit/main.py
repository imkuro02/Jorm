from pyvis.network import Network
import networkx as nx

# Create a graph object using NetworkX
G = nx.Graph()

# Add nodes with values
G.add_node(1, value=10)
G.add_node(2, value=20)
G.add_node(3, value=30)
G.add_node(4, value=40)

# Add edges between the nodes
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])

# Create a pyvis network object
net = Network(height='750px', width='100%', notebook=True)

# Transfer the graph from NetworkX to pyvis
net.from_nx(G)

# Set some options to customize the network
net.set_options("""
var options = {
  "nodes": {
    "borderWidth": 2,
    "borderWidthSelected": 4,
    "shape": "dot",
    "size": 10,
    "color": {
      "background": "#00f",
      "border": "#00f"
    }
  },
  "edges": {
    "width": 2,
    "color": {
      "highlight": "#ff0000",
      "inherit": true
    },
    "smooth": {
      "enabled": true,
      "type": "continuous"
    }
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -2000,
      "springLength": 95
    }
  }
}
""")

# Save and show the network
net.show("interactive_network.html")

