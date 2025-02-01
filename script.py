import spacy
import pdfplumber
import networkx as nx
import re
import difflib
import plotly.graph_objects as go


nlp = spacy.load("en_core_web_md")


allowed_entity_types = ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "NORP", "FACILITY", "LAW"]


custom_acronyms = {"ATCS", "UNMIK", "KTA", "ITF", "PEAP", "PISG", "DSA", "Pillar IV"}


def extract_text_with_format(pdf_path):
    structured_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            for word in words:
                structured_text.append(word["text"])
            tables = page.extract_tables()
            for table in tables:
                structured_text.append("[TABLE] " + str(table))
    return "\n".join(structured_text)


def extract_entities(text):
    doc = nlp(text)
    named_entities = {ent.text.strip(): ent.label_ for ent in doc.ents if ent.label_ in allowed_entity_types}
    noun_chunks = {chunk.text.strip(): "NOUN_CHUNK" for chunk in doc.noun_chunks if len(chunk.text.split()) > 1}
    detected_acronyms = {match: "ACRONYM" for match in re.findall(r'\b[A-Z]{2,5}\b', text) if match in custom_acronyms}
    
    combined_entities = {**named_entities, **noun_chunks, **detected_acronyms}
    refined_entities = {k: v for k, v in combined_entities.items() if len(k) > 2 and not k.isdigit()}
    
    return list(set(refined_entities.keys()))

def is_valid_entity(entity, entity_list):
    return bool(difflib.get_close_matches(entity, entity_list, n=1, cutoff=0.75))

def extract_spacy_relationships(sent, entity_list):
    doc = nlp(sent.text)
    relationships = []
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass", "agent", "nmod", "acl", "advcl") and token.head.pos_ == "VERB":
            subject = token.text
            verb = token.head.lemma_
            objects = [child.text for child in token.head.children if child.dep_ in ("dobj", "pobj", "attr", "prep")]
            for obj in objects:
                if is_valid_entity(subject, entity_list) and is_valid_entity(obj, entity_list):
                    if subject.lower() not in ["he", "she", "it", "that", "they"] and obj.lower() not in ["it", "that"]:
                        relationships.append((subject, verb, obj))
    if "[HEADER]" in sent.text:
        relationships.append(("Document", "discusses", sent.text.replace("[HEADER]", "").strip()))
    return relationships

def extract_table_relationships(text, entity_list):
    relationships = []
    for line in text.split("\n"):
        if "[TABLE]" in line:
            try:
                table_data = line.replace("[TABLE]", "").strip()
                rows = table_data.split("],[")
                for row in rows:
                    cols = row.strip("[]").split(",")
                    if len(cols) >= 2:
                        subj, obj = cols[0].strip("'"), cols[1].strip("'")
                        if is_valid_entity(subj, entity_list) and is_valid_entity(obj, entity_list):
                            relationships.append((subj, "is associated with", obj))
            except Exception as e:
                continue
    return relationships


pdf_file_path = "YOUR_PDF_HERE.pdf"  # Update this path to your PDF file
text = extract_text_with_format(pdf_file_path)


entity_list = extract_entities(text)
relationships = []
for sent in nlp(text).sents:
    relationships.extend(extract_spacy_relationships(sent, entity_list))
relationships.extend(extract_table_relationships(text, entity_list))

print("\n### FINAL Extracted Entities ###")
print(entity_list)

print("\n### FINAL Improved Relationships ###")
for r in relationships:
    print(r)

def visualize_relationships_plotly(classified_relationships):
    G = nx.DiGraph()
    for subj, relation, obj in classified_relationships:
        G.add_edge(subj, obj, label=relation)
    
    pos = nx.spring_layout(G, seed=42, k=0.8)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, 
        y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_sizes = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        degree = G.degree[node]
        node_sizes.append(15 + degree * 10)
        
    node_trace = go.Scatter(
        x=node_x, 
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=node_sizes,
            color='#6175c1',
            line=dict(width=2)
        )
    )
    
    edge_annotations = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        label = edge[2]['label']
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        edge_annotations.append(
            dict(
                x=xm,
                y=ym,
                text=label,
                showarrow=False,
                font=dict(color="red", size=10),
                xanchor="center",
                yanchor="middle"
            )
        )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Enhanced Entity Relationship Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=edge_annotations,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    
    fig.show()

visualize_relationships_plotly(relationships)
