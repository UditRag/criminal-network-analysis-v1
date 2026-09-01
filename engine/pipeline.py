import os
import re
import pandas as pd
from rapidfuzz import fuzz

def extract_entities_from_text(text, source_id):
    entities = []
    phones = re.findall(r'\b\d{10}\b', text)
    for p in phones:
        entities.append({"entity": p, "type": "PHONE", "source": source_id, "evidence": text})
    
    names = re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text)
    for n in names:
        if n not in ["Bhopal Railway", "New Delhi"]: 
            entities.append({"entity": n, "type": "PERSON", "source": source_id, "evidence": text})
            
    return entities

def resolve_entities(entities_df):
    entities_df['canonical'] = entities_df['entity'].str.lower().str.strip()
    unique_entities = entities_df['canonical'].unique()
    resolution_map = {}
    
    for i in range(len(unique_entities)):
        if unique_entities[i] in resolution_map: continue
        resolution_map[unique_entities[i]] = unique_entities[i]
        
        for j in range(i + 1, len(unique_entities)):
            if unique_entities[j] in resolution_map: continue
            score = fuzz.ratio(unique_entities[i], unique_entities[j])
            if score > 85: 
                resolution_map[unique_entities[j]] = unique_entities[i]
                
    entities_df['canonical'] = entities_df['canonical'].map(resolution_map)
    entities_df['canonical'] = entities_df['canonical'].apply(lambda x: x.title() if not x.isdigit() else x)
    return entities_df

def process_demo_data():
    all_entities = []
    relationships = []
    
    fir_files = [f for f in os.listdir("data/demo") if f.endswith(".txt")]
    for file in fir_files:
        with open(f"data/demo/{file}", "r") as f:
            text = f.read()
            ext = extract_entities_from_text(text, file)
            all_entities.extend(ext)
            for i in range(len(ext)):
                for j in range(i+1, len(ext)):
                    relationships.append({
                        "source": ext[i]['entity'], "target": ext[j]['entity'],
                        "type": "MENTIONED_WITH", "doc": file, "evidence": text
                    })

    cdr_df = pd.read_csv("data/demo/cdr.csv")
    for _, row in cdr_df.iterrows():
        all_entities.extend([
            {"entity": str(row['caller']), "type": "PHONE", "source": "cdr.csv", "evidence": f"{row['calls']} calls"},
            {"entity": str(row['receiver']), "type": "PHONE", "source": "cdr.csv", "evidence": f"{row['calls']} calls"}
        ])
        relationships.append({
            "source": str(row['caller']), "target": str(row['receiver']),
            "type": "CONTACTED", "doc": "cdr.csv", "evidence": f"{row['calls']} calls on {row['date']}",
            "weight": row['calls'], "date": row['date']
        })

    fin_df = pd.read_csv("data/demo/transactions.csv")
    for _, row in fin_df.iterrows():
        all_entities.extend([
            {"entity": row['sender'], "type": "PERSON", "source": "transactions.csv", "evidence": row['transaction_id']},
            {"entity": row['receiver'], "type": "PERSON", "source": "transactions.csv", "evidence": row['transaction_id']}
        ])
        relationships.append({
            "source": row['sender'], "target": row['receiver'],
            "type": "TRANSFERRED_MONEY", "doc": "transactions.csv", "evidence": f"{row['transaction_id']}: {row['amount']}",
            "amount": row['amount']
        })

    ent_df = pd.DataFrame(all_entities)
    ent_df = resolve_entities(ent_df)
    
    rel_df = pd.DataFrame(relationships)
    canonical_map = dict(zip(ent_df['entity'], ent_df['canonical']))
    rel_df['source'] = rel_df['source'].map(canonical_map).fillna(rel_df['source'])
    rel_df['target'] = rel_df['target'].map(canonical_map).fillna(rel_df['target'])
    
    return ent_df, rel_df
