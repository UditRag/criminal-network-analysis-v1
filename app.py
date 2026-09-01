import streamlit as st
import pandas as pd
import networkx as nx
from engine.demo_data import generate_demo_data
from engine.pipeline import process_demo_data
from engine.analytics import build_graph, detect_anomalies
from engine.visualization import generate_network_html
import streamlit.components.v1 as components

st.set_page_config(page_title="Criminal Network Analysis", layout="wide")

if 'processed' not in st.session_state:
    st.session_state.processed = False

st.sidebar.title("SIH26189 Prototype")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Dashboard & Network", "Alerts & Evidence", "Entity Search"])

st.sidebar.markdown("---")
if st.sidebar.button("LOAD DEMO INVESTIGATION", type="primary"):
    with st.spinner("Generating synthetic data and processing pipeline..."):
        generate_demo_data()
        ent_df, rel_df = process_demo_data()
        G = build_graph(rel_df)
        alerts_df = detect_anomalies(ent_df, rel_df, G)
        
        st.session_state.ent_df = ent_df
        st.session_state.rel_df = rel_df
        st.session_state.G = G
        st.session_state.alerts_df = alerts_df
        st.session_state.processed = True
    st.sidebar.success("Pipeline executed successfully!")

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
st.sidebar.warning(
    "**Disclaimer:** This is a decision-support prototype. "
    "It identifies potentially relevant patterns for human review using synthetic data. "
    "It does not determine guilt or legal conclusions."
)

if not st.session_state.processed:
    st.title("AI-Powered Criminal Network Analysis System")
    st.info("👈 Click **'LOAD DEMO INVESTIGATION'** in the sidebar to run the V1 pipeline.")
else:
    ent_df = st.session_state.ent_df
    rel_df = st.session_state.rel_df
    G = st.session_state.G
    alerts_df = st.session_state.alerts_df

    if nav == "Dashboard & Network":
        st.title("Investigation Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Entities", len(G.nodes))
        col2.metric("Total Relationships", len(G.edges))
        col3.metric("Suspicious Alerts", len(alerts_df))
        col4.metric("Evidence Documents", ent_df['source'].nunique())
        
        st.markdown("---")
        st.subheader("Interactive Network Graph")
        html_path = generate_network_html(G)
        with open(html_path, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=620)
        
        st.caption("Legend: 🔴 Red = Financial | 🔵 Blue = Communication | ⚪ Gray = Mentioned Together")

    elif nav == "Alerts & Evidence":
        st.title("Suspicious Pattern Alerts")
        
        if alerts_df.empty:
            st.success("No anomalies detected.")
        else:
            for _, row in alerts_df.iterrows():
                with st.expander(f"🚨 {row['priority']} PRIORITY: {row['entity']} - {row['type']}", expanded=True):
                    st.write(f"**WHY FLAGGED?** {row['reason']}")
                    st.code(row['evidence'], language="text")

    elif nav == "Entity Search":
        st.title("Entity Deep-Dive")
        search_query = st.selectbox("Select an Entity:", sorted(list(G.nodes)))
        
        if search_query:
            st.subheader(f"Profile: {search_query}")
            st.write(f"**Total connections:** {G.degree(search_query)}")
            
            entity_alerts = alerts_df[alerts_df['entity'] == search_query]
            if not entity_alerts.empty:
                st.error(f"⚠️ Flagged for: {', '.join(entity_alerts['type'].tolist())}")
                
            st.markdown("### Known Relationships")
            entity_rels = rel_df[(rel_df['source'] == search_query) | (rel_df['target'] == search_query)]
            st.dataframe(entity_rels[['source', 'target', 'type', 'doc', 'evidence']], use_container_width=True)
            
            st.markdown("---")
            st.subheader("Find Connection")
            target_query = st.selectbox("Find path to:", sorted([n for n in G.nodes if n != search_query]))
            
            if st.button("Find Shortest Path"):
                try:
                    path = nx.shortest_path(G.to_undirected(), source=search_query, target=target_query)
                    st.success(f"Path found! Length: {len(path)-1} degrees of separation.")
                    st.code(" -> ".join(path), language="text")
                except nx.NetworkXNoPath:
                    st.warning("No known connection between these entities.")
