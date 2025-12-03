"""Fetch PubMed abstracts"""
from Bio import Entrez
import json
from pathlib import Path
import time

Entrez.email = "your.email@example.com"

def fetch_pubmed_abstracts(query, max_results=1000, output_file=None):
    """Fetch PubMed abstracts"""
    print(f"Searching PubMed for: {query}")
    
    # Search
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    
    id_list = record["IdList"]
    print(f"Found {len(id_list)} papers")
    
    abstracts = []
    
    # Fetch details in batches
    batch_size = 100
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i+batch_size]
        
        try:
            handle = Entrez.efetch(db="pubmed", id=batch_ids, 
                                  rettype="abstract", retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            
            for article in records['PubmedArticle']:
                try:
                    medline = article['MedlineCitation']
                    article_data = medline['Article']
                    
                    # Extract abstract
                    if 'Abstract' in article_data:
                        abstract_text = ' '.join([
                            text for text in article_data['Abstract']['AbstractText']
                        ])
                    else:
                        continue
                    
                    abstracts.append({
                        'pmid': str(medline['PMID']),
                        'title': article_data.get('ArticleTitle', ''),
                        'abstract': abstract_text,
                        'journal': article_data.get('Journal', {}).get('Title', ''),
                        'year': article_data.get('ArticleDate', [{}])[0].get('Year', '')
                    })
                except:
                    continue
            
            time.sleep(0.5)  # Rate limiting
            print(f"Processed {min(i+batch_size, len(id_list))}/{len(id_list)}")
            
        except Exception as e:
            print(f"Error in batch {i}: {e}")
            continue
    
    # Save
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(abstracts, f, indent=2)
        print(f"Saved {len(abstracts)} abstracts to {output_file}")
    
    return abstracts

if __name__ == "__main__":
    # Example queries
    queries = [
        "cardiovascular disease",
        "diabetes mellitus",
        "respiratory disease",
        "cancer treatment"
    ]
    
    all_abstracts = []
    for query in queries:
        abstracts = fetch_pubmed_abstracts(query, max_results=2000)
        all_abstracts.extend(abstracts)
    
    # Save combined
    with open("data/raw/pubmed_abstracts.json", 'w') as f:
        json.dump(all_abstracts, f, indent=2)
    
    print(f"Total abstracts collected: {len(all_abstracts)}")
