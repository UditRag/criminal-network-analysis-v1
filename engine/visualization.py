from pyvis.network import Network
import networkx as nx

def generate_network_html(G, output_path="network.html"):
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
    for node in G.nodes():
        degree = G.degree(node)
        net.add_node(node, label=str(node), title=f"Connections: {degree}", size=15 + (degree*2))
        
    for source, target, data in G.edges(data=True):
        color = "gray"
        if data.get('relationship') == "TRANSFERRED_MONEY": color = "red"
        elif data.get('relationship') == "CONTACTED": color = "blue"
        
        net.add_edge(source, target, title=f"{data.get('relationship')}\n{data.get('evidence')}", color=color)
        
    net.set_options("""
    var options = {
      "physics": { "barnesHut": { "gravitationalConstant": -30000, "springLength": 200 } }
    }
    """)
    net.write_html(output_path)
    return output_path
