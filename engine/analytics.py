import networkx as nx
import pandas as pd

def build_graph(relationships_df):
    G = nx.DiGraph()
    for _, row in relationships_df.iterrows():
        G.add_edge(row['source'], row['target'], 
                   relationship=row['type'], 
                   evidence=row['evidence'], 
                   doc=row['doc'])
    return G

def detect_anomalies(entities_df, relationships_df, G):
    alerts = []
    
    source_counts = entities_df.groupby('canonical')['source'].nunique()
    multi_source = source_counts[source_counts >= 3].index
    for entity in multi_source:
        sources = entities_df[entities_df['canonical'] == entity]['source'].unique()
        alerts.append({
            "entity": entity, "type": "MULTI-SOURCE CROSSOVER", "priority": "Medium",
            "reason": "Entity appears across multiple intelligence streams.",
            "evidence": f"Found in: {', '.join(sources)}"
        })

    cdr_rels = relationships_df[relationships_df['type'] == 'CONTACTED']
    if not cdr_rels.empty:
        spikes = cdr_rels[cdr_rels['weight'] >= 50]
        for _, row in spikes.iterrows():
            alerts.append({
                "entity": row['source'], "type": "COMMUNICATION SPIKE", "priority": "High",
                "reason": f"Abnormal communication volume detected on {row['date']}.",
                "evidence": f"Detected: {row['weight']} calls to {row['target']}."
            })

    fin_rels = relationships_df[relationships_df['type'] == 'TRANSFERRED_MONEY']
    if not fin_rels.empty:
        fin_G = nx.DiGraph()
        for _, row in fin_rels.iterrows():
            fin_G.add_edge(row['source'], row['target'], amount=row['amount'])
        
        cycles = list(nx.simple_cycles(fin_G))
        for cycle in cycles:
            if len(cycle) > 2: 
                for node in cycle:
                    alerts.append({
                        "entity": node, "type": "CIRCULAR MONEY FLOW", "priority": "High",
                        "reason": "Entity is part of a closed-loop financial cycle.",
                        "evidence": f"Cycle detected: {' -> '.join(cycle)} -> {cycle[0]}"
                    })

    if len(G.nodes) > 0:
        centrality = nx.betweenness_centrality(G.to_undirected())
        for node, score in centrality.items():
            if score > 0.4: 
                alerts.append({
                    "entity": node, "type": "BRIDGE ENTITY", "priority": "Medium",
                    "reason": "Entity connects distinct, otherwise isolated groups.",
                    "evidence": f"Centrality Score: {score:.2f}. Connects {G.degree(node)} points."
                })
                
    seen = set()
    unique_alerts = []
    for alert in alerts:
        identifier = f"{alert['entity']}_{alert['type']}"
        if identifier not in seen:
            seen.add(identifier)
            unique_alerts.append(alert)
            
    return pd.DataFrame(unique_alerts)
