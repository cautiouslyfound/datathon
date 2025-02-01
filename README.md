# Entity Extraction and Relationship Visualization

## Overview
This project extracts entities and relationships from unstructured text in PDF files and visualizes them as a network graph. It uses Natural Language Processing (NLP) with spaCy for entity extraction and dependency parsing, and NetworkX with Plotly for interactive visualization.

## Features
- Extracts named entities (PERSON, ORG, GPE, etc.) from PDF documents.
- Identifies and filters acronyms based on a predefined list.
- Extracts subject-verb-object relationships using dependency parsing.
- Processes tables from PDFs to extract meaningful relationships.
- Visualizes the extracted entities and relationships using Plotly.

## Requirements
Ensure you have the following dependencies installed:

```bash
pip install spacy pdfplumber networkx plotly
python -m spacy download en_core_web_md
```

## Usage
### 1. Place the PDF File
Update the variable `pdf_file_path` in the script with the path to your PDF file:

```python
pdf_file_path = "YOUR_PDF_HERE.pdf"
```

### 2. Run the Script
Execute the script to extract entities and relationships:

```bash
python script.py
```

### 3. View Extracted Entities and Relationships
The script will output extracted entities and relationships in the console.

### 4. Interactive Visualization
A network graph will be displayed showing the relationships between entities.

## Key Functions
### `extract_text_with_format(pdf_path)`
Extracts text from PDFs, including tables and structured data.

### `extract_entities(text)`
Identifies named entities, noun chunks, and acronyms from the text.

### `extract_spacy_relationships(sent, entity_list)`
Extracts relationships using dependency parsing (e.g., subject-verb-object structures).

### `extract_table_relationships(text, entity_list)`
Parses table data and extracts relevant relationships.

### `visualize_relationships_plotly(classified_relationships)`
Generates an interactive network graph using Plotly.

## Example Output
```
### FINAL Extracted Entities ###
['John Doe', 'IBM', 'New York']

### FINAL Improved Relationships ###
('John Doe', 'works at', 'IBM')
('IBM', 'is based in', 'New York')
```

## Customization
- Modify `allowed_entity_types` to include additional entity types.
- Add or remove acronyms in `custom_acronyms`.
- Adjust the dependency parsing rules in `extract_spacy_relationships()` for better accuracy.

## License
This project is open-source and available for use under the MIT License.
