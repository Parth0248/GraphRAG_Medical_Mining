"""Interactive Knowledge Graph Visualization for GraphRAG Medical Mining

Creates beautiful 3D interactive visualizations of the medical knowledge graph
using PyVis and Plotly.
"""

from neo4j import GraphDatabase
from pyvis.network import Network
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path
import json


class GraphVisualizer:
    """Interactive knowledge graph visualization"""
    
    def __init__(self, uri, username, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    def get_subgraph_around_entity(self, entity_name: str, max_depth: int = 2):
        """Extract subgraph around a specific entity"""
        with self.driver.session() as session:
            # Note: max_depth must be literal in Cypher relationship pattern
            query = f"""
                MATCH path = (start:Entity {{name: $entity_name}})-[*1..{max_depth}]-(connected)
                WITH relationships(path) as rels, nodes(path) as nodes
                UNWIND rels as rel
                WITH startNode(rel) as source, endNode(rel) as target, type(rel) as rel_type
                RETURN DISTINCT 
                    id(source) as source_id,
                    source.name as source_name,
                    labels(source)[0] as source_type,
                    id(target) as target_id,
                    target.name as target_name,
                    labels(target)[0] as target_type,
                    rel_type
                """
            
            result = session.run(query, entity_name=entity_name)
            
            nodes = {}
            edges = []
            
            for record in result:
                # Add source node (with null check)
                source_id = record['source_id']
                source_name = record['source_name']
                
                if source_name is None or source_name == '':
                    continue  # Skip nodes without names
                
                if source_id not in nodes:
                    nodes[source_id] = {
                        'id': source_id,
                        'name': source_name,
                        'type': record['source_type']
                    }
                
                # Add target node (with null check)
                target_id = record['target_id']
                target_name = record['target_name']
                
                if target_name is None or target_name == '':
                    continue  # Skip nodes without names
                
                if target_id not in nodes:
                    nodes[target_id] = {
                        'id': target_id,
                        'name': target_name,
                        'type': record['target_type']
                    }
                
                # Add edge only if both nodes have names
                if source_name and target_name:
                    edges.append({
                        'source': source_id,
                        'target': target_id,
                        'type': record['rel_type']
                    })
            
            return list(nodes.values()), edges
    
    def create_pyvis_network(self, nodes, edges, output_file='results/graph_viz.html'):
        """Create interactive 2D network using PyVis"""
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        
        # Set physics options
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 200,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
          }
        }
        """)
        
        # Color mapping for entity types
        color_map = {
            'Disease': '#ff6b6b',
            'Drug': '#4ecdc4',
            'Medication': '#4ecdc4',
            'Symptom': '#ffd700',
            'Sign_symptom': '#ffd700',
            'Disease_disorder': '#ff6b6b',
            'Procedure': '#95e1d3',
            'Diagnostic_procedure': '#95e1d3',
            'Entity': '#a8dadc',
            'Document': '#457b9d'
        }
        
        # Add nodes
        for node in nodes:
            entity_type = node.get('type', 'Entity')
            color = color_map.get(entity_type, '#cccccc')
            
            net.add_node(
                node['id'],
                label=node['name'],
                title=f"{entity_type}: {node['name']}",
                color=color,
                size=20 + len(node['name'])  # Size based on name length
            )
        
        # Add edges
        edge_colors = {
            'MENTIONED_IN': '#666666',
            'CO_OCCURS_WITH': '#999999',
            'HAS_SYMPTOM': '#ffd700',
            'TREATED_BY': '#4ecdc4'
        }
        
        for edge in edges:
            color = edge_colors.get(edge['type'], '#888888')
            net.add_edge(
                edge['source'],
                edge['target'],
                title=edge['type'],
                color=color
            )
        
        # Save
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        net.save_graph(str(output_file))
        
        print(f"✅ Interactive graph saved: {output_file}")
        return output_file
    
    def create_3d_plotly_graph(self, nodes, edges, output_file='results/graph_3d.html'):
        """Create 3D interactive network using Plotly"""
        # Create NetworkX graph for layout
        G = nx.Graph()
        for node in nodes:
            G.add_node(node['id'], **node)
        for edge in edges:
            G.add_edge(edge['source'], edge['target'], **edge)
        
        # Get 3D spring layout
        pos_3d = nx.spring_layout(G, dim=3, k=0.5, iterations=50)
        
        # Extract coordinates
        edge_x = []
        edge_y = []
        edge_z = []
        
        for edge in edges:
            x0, y0, z0 = pos_3d[edge['source']]
            x1, y1, z1 = pos_3d[edge['target']]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_z += [z0, z1, None]
        
        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color='#888', width=1),
            hoverinfo='none'
        )
        
        # Node coordinates and colors
        node_x = []
        node_y = []
        node_z = []
        node_colors = []
        node_text = []
        
        color_map = {
            'Disease': 'red',
            'Drug': 'cyan',
            'Medication': 'cyan',
            'Symptom': 'gold',
            'Sign_symptom': 'gold',
            'Disease_disorder': 'red',
            'Procedure': 'lightgreen',
            'Entity': 'lightblue',
            'Document': 'steelblue'
        }
        
        for node in nodes:
            x, y, z = pos_3d[node['id']]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            
            entity_type = node.get('type', 'Entity')
            node_colors.append(color_map.get(entity_type, 'gray'))
            node_text.append(f"{node['name']}<br>Type: {entity_type}")
        
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            marker=dict(
                size=10,
                color=node_colors,
                line=dict(color='white', width=0.5)
            ),
            text=[n['name'] for n in nodes],
            textposition='top center',
            hovertext=node_text,
            hoverinfo='text'
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace])
        
        fig.update_layout(
            title='3D Medical Knowledge Graph',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            scene=dict(
                xaxis=dict(showgrid=False, showticklabels=False, title=''),
                yaxis=dict(showgrid=False, showticklabels=False, title=''),
                zaxis=dict(showgrid=False, showticklabels=False, title='')
            ),
            template='plotly_dark'
        )
        
        # Save
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_file))
        
        print(f"✅ 3D graph saved: {output_file}")
        return output_file


def visualize_entity(entity_name: str, uri, username, password):
    """Visualize subgraph around an entity"""
    print(f"\n📊 Creating visualization for: {entity_name}")
    
    viz = GraphVisualizer(uri, username, password)
    
    # Get subgraph
    nodes, edges = viz.get_subgraph_around_entity(entity_name, max_depth=2)
    
    print(f"   Found: {len(nodes)} nodes, {len(edges)} edges")
    
    # Create 2D interactive graph
    output_2d = viz.create_pyvis_network(nodes, edges, f'results/graph_{entity_name.lower()}_2d.html')
    
    # Create 3D graph
    output_3d = viz.create_3d_plotly_graph(nodes, edges, f'results/graph_{entity_name.lower()}_3d.html')
    
    viz.close()
    
    return output_2d, output_3d


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    
    print("="*70)
    print("       Interactive Knowledge Graph Visualization")
    print("="*70)
    
    # Example: Visualize "diabetes" subgraph
    entity = "diabetes"
    
    try:
        output_2d, output_3d = visualize_entity(entity, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        
        print("\n✅ Visualization complete!")
        print(f"\n   2D Interactive: {output_2d}")
        print(f"   3D Interactive: {output_3d}")
        print("\n   Open these files in your browser to explore!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Neo4j is running")
        print("  2. Graph has been populated")
        print("  3. Entity 'diabetes' exists in the graph")
