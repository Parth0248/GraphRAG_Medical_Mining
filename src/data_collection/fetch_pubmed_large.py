"""Large-scale PubMed data collection for GraphRAG Medical Mining

This script fetches 1000+ medical abstracts from PubMed in specific categories:
- Cardiovascular diseases
- Diabetes and metabolism
- Respiratory diseases
- Oncology
- Neurology

Uses Biopython Entrez API with rate limiting to respect NCBI guidelines.
"""

from Bio import Entrez
import json
from pathlib import Path
import time
from tqdm import tqdm
import sys

# NCBI requires email for API access
Entrez.email = "your.email@example.com"  # TODO: Replace with actual email

class PubMedLargeFetcher:
    def __init__(self, email="graphrag.medical@example.com"):
        """Initialize PubMed fetcher with email for API"""
        Entrez.email = email
        self.abstracts = []
        
    def search_pubmed(self, query, max_results=200, retstart=0):
        """Search PubMed and return list of PMIDs"""
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                retstart=retstart,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()
            return record["IdList"]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def fetch_abstracts(self, pmid_list, batch_size=50):
        """Fetch full abstract details for list of PMIDs"""
        abstracts = []
        
        for i in tqdm(range(0, len(pmid_list), batch_size), desc="Fetching abstracts"):
            batch = pmid_list[i:i+batch_size]
            try:
                handle = Entrez.efetch(
                    db="pubmed",
                    id=batch,
                    rettype="abstract",
                    retmode="xml"
                )
                records = Entrez.read(handle)
                handle.close()
                
                for record in records['PubmedArticle']:
                    try:
                        article = record['MedlineCitation']['Article']
                        pmid = str(record['MedlineCitation']['PMID'])
                        
                        # Extract title
                        title = article.get('ArticleTitle', '')
                        
                        # Extract abstract (may have multiple parts)
                        abstract_parts = []
                        if 'Abstract' in article:
                            if 'AbstractText' in article['Abstract']:
                                abstract_text = article['Abstract']['AbstractText']
                                if isinstance(abstract_text, list):
                                    abstract_parts = [str(part) for part in abstract_text]
                                else:
                                    abstract_parts = [str(abstract_text)]
                        
                        abstract = ' '.join(abstract_parts)
                        
                        # Extract year
                        year = ''
                        if 'Journal' in article:
                            if 'JournalIssue' in article['Journal']:
                                if 'PubDate' in article['Journal']['JournalIssue']:
                                    pub_date = article['Journal']['JournalIssue']['PubDate']
                                    year = pub_date.get('Year', '')
                        
                        # Extract MeSH terms if available
                        mesh_terms = []
                        if 'MeshHeadingList' in record['MedlineCitation']:
                            for mesh in record['MedlineCitation']['MeshHeadingList']:
                                if 'DescriptorName' in mesh:
                                    mesh_terms.append(str(mesh['DescriptorName']))
                        
                        # Only add if has abstract and title
                        if abstract and title:
                            abstracts.append({
                                'pmid': pmid,
                                'title': title,
                                'abstract': abstract,
                                'year': year,
                                'mesh_terms': mesh_terms
                            })
                    
                    except Exception as e:
                        print(f"Error parsing article: {e}")
                        continue
                
                # Rate limiting - NCBI allows 3 requests/second
                time.sleep(0.4)
                
            except Exception as e:
                print(f"Batch fetch error: {e}")
                time.sleep(2)  # Back off on error
                continue
        
        return abstracts
    
    def collect_by_category(self, category, query, target_count=200):
        """Collect abstracts for a specific medical category"""
        print(f"\n📚 Collecting {category} abstracts...")
        print(f"   Query: {query}")
        
        all_pmids = []
        batch_size = 100
        
        # Search in batches
        for start in range(0, target_count, batch_size):
            pmids = self.search_pubmed(query, max_results=batch_size, retstart=start)
            all_pmids.extend(pmids)
            time.sleep(0.4)
            
            if len(pmids) < batch_size:
                break  # No more results
        
        print(f"   Found {len(all_pmids)} PMIDs")
        
        # Fetch abstract details
        abstracts = self.fetch_abstracts(all_pmids[:target_count])
        
        print(f"   ✅ Retrieved {len(abstracts)} complete abstracts")
        return abstracts
    
    def collect_all_categories(self):
        """Collect abstracts across all medical categories"""
        
        categories = {
            'Cardiovascular': {
                'query': '(cardiovascular disease OR hypertension OR heart failure OR myocardial infarction) AND (treatment OR therapy OR diagnosis)',
                'count': 300
            },
            'Diabetes': {
                'query': '(diabetes mellitus OR type 2 diabetes OR insulin resistance OR hyperglycemia) AND (treatment OR management OR pathophysiology)',
                'count': 300
            },
            'Respiratory': {
                'query': '(asthma OR COPD OR pneumonia OR respiratory disease) AND (treatment OR diagnosis OR pathophysiology)',
                'count': 200
            },
            'Oncology': {
                'query': '(cancer OR carcinoma OR tumor OR neoplasm) AND (treatment OR chemotherapy OR immunotherapy)',
                'count': 200
            },
            'Neurology': {
                'query': '(alzheimer OR parkinson OR multiple sclerosis OR stroke OR dementia) AND (treatment OR diagnosis OR pathophysiology)',
                'count': 150
            },
            'Endocrine': {
                'query': '(thyroid disorder OR hypothyroidism OR hyperthyroidism OR endocrine disease) AND (treatment OR diagnosis)',
                'count': 100
            },
            'Gastroenterology': {
                'query': '(inflammatory bowel disease OR GERD OR gastritis OR hepatitis) AND (treatment OR diagnosis)',
                'count': 100
            },
            'Rheumatology': {
                'query': '(rheumatoid arthritis OR lupus OR autoimmune disease OR osteoarthritis) AND (treatment OR diagnosis)',
                'count': 100
            }
        }
        
        all_abstracts = []
        
        for category, params in categories.items():
            try:
                abstracts = self.collect_by_category(
                    category=category,
                    query=params['query'],
                    target_count=params['count']
                )
                
                # Tag with category
                for abstract in abstracts:
                    abstract['category'] = category
                
                all_abstracts.extend(abstracts)
                
                # Save checkpoint after each category
                self.save_checkpoint(all_abstracts, category)
                
            except Exception as e:
                print(f"❌ Error collecting {category}: {e}")
                continue
        
        return all_abstracts
    
    def save_checkpoint(self, abstracts, category):
        """Save checkpoint after each category"""
        checkpoint_dir = Path("data/raw/checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint_{category.lower()}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(abstracts, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Checkpoint saved: {len(abstracts)} total abstracts")
    
    def deduplicate(self, abstracts):
        """Remove duplicate PMIDs"""
        seen = set()
        unique = []
        
        for abstract in abstracts:
            if abstract['pmid'] not in seen:
                seen.add(abstract['pmid'])
                unique.append(abstract)
        
        print(f"\n🔄 Deduplication: {len(abstracts)} → {len(unique)} abstracts")
        return unique
    
    def save_final(self, abstracts, filename="pubmed_abstracts_large.json"):
        """Save final dataset"""
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(abstracts, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Final dataset saved: {output_file}")
        print(f"   Total abstracts: {len(abstracts)}")
        
        # Print statistics
        print("\n📊 Dataset Statistics:")
        print(f"   Total documents: {len(abstracts)}")
        
        # Count by category
        categories = {}
        for abstract in abstracts:
            cat = abstract.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n   By Category:")
        for cat, count in sorted(categories.items()):
            print(f"   - {cat}: {count} abstracts")
        
        # Count with MeSH terms
        with_mesh = sum(1 for a in abstracts if a.get('mesh_terms'))
        print(f"\n   With MeSH terms: {with_mesh} ({100*with_mesh/len(abstracts):.1f}%)")
        
        return output_file

def main():
    """Main execution function"""
    print("=" * 70)
    print("      PubMed Large-Scale Data Collection for GraphRAG")
    print("=" * 70)
    print("\nTarget: 1,000+ medical research abstracts")
    print("Categories: Cardiovascular, Diabetes, Respiratory, Oncology, etc.")
    print("\n⚠️  Note: This will take approximately 30-60 minutes due to API rate limits")
    print("=" * 70)
    
    # Prompt for email
    email = input("\nEnter your email for NCBI API (required): ").strip()
    if not email or '@' not in email:
        print("❌ Valid email required for NCBI Entrez API")
        sys.exit(1)
    
    fetcher = PubMedLargeFetcher(email=email)
    
    # Collect all abstracts
    print("\n🚀 Starting data collection...")
    abstracts = fetcher.collect_all_categories()
    
    # Deduplicate
    abstracts = fetcher.deduplicate(abstracts)
    
    # Save final dataset
    output_file = fetcher.save_final(abstracts)
    
    print("\n" + "=" * 70)
    print("✅ Data collection complete!")
    print(f"📁 Output file: {output_file}")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run: python src/graph_construction/build_graph.py")
    print("2. This will populate Neo4j with the expanded dataset")
    print("=" * 70)

if __name__ == "__main__":
    main()
