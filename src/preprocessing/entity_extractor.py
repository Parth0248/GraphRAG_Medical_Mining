"""Simplified Medical Entity Extraction without scispacy"""
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re

class MedicalEntityExtractor:
    def __init__(self):
        """Initialize entity extractor with BioBERT NER"""
        print("Loading BioBERT NER model...")
        try:
            # Use a pre-trained biomedical NER model
            self.tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
            self.model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
            self.ner_pipeline = pipeline(
                "ner", 
                model=self.model, 
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            print("✓ BioBERT NER model loaded")
        except Exception as e:
            print(f"Warning: Could not load BioBERT NER: {e}")
            print("Using simple keyword extraction instead")
            self.ner_pipeline = None
    
    def simple_extraction(self, text):
        """Fallback: Simple keyword-based entity extraction"""
        entities = []
        
        # Medical keywords (sample list)
        diseases = ['diabetes', 'hypertension', 'asthma', 'cancer', 'covid', 'pneumonia', 
                   'arthritis', 'alzheimer', 'parkinson', 'stroke', 'heart disease']
        drugs = ['metformin', 'aspirin', 'insulin', 'ibuprofen', 'acetaminophen',
                'lisinopril', 'atorvastatin', 'omeprazole', 'albuterol']
        symptoms = ['fever', 'cough', 'pain', 'fatigue', 'nausea', 'headache',
                   'dizziness', 'shortness of breath', 'chest pain']
        
        text_lower = text.lower()
        
        # Find diseases
        for disease in diseases:
            if disease in text_lower:
                start = text_lower.find(disease)
                entities.append({
                    'text': disease.title(),
                    'label': 'Disease',
                    'score': 0.9,
                    'start': start,
                    'end': start + len(disease)
                })
        
        # Find drugs
        for drug in drugs:
            if drug in text_lower:
                start = text_lower.find(drug)
                entities.append({
                    'text': drug.title(),
                    'label': 'Drug',
                    'score': 0.9,
                    'start': start,
                    'end': start + len(drug)
                })
        
        # Find symptoms
        for symptom in symptoms:
            if symptom in text_lower:
                start = text_lower.find(symptom)
                entities.append({
                    'text': symptom.title(),
                    'label': 'Symptom',
                    'score': 0.9,
                    'start': start,
                    'end': start + len(symptom)
                })
        
        return entities
    
    def extract_entities(self, text):
        """Extract medical entities from text"""
        entities = []
        
        if self.ner_pipeline:
            try:
                # Use BioBERT NER
                ner_results = self.ner_pipeline(text[:512])  # Limit text length
                
                for ent in ner_results:
                    text_clean = ent['word'].strip()
                    # Filter trash tokens
                    if text_clean.startswith("##") or "##" in text_clean or len(text_clean) < 2 or not text_clean[0].isalnum():
                        continue
                        
                    entities.append({
                        'text': text_clean,
                        'label': ent['entity_group'],
                        'score': ent['score'],
                        'start': ent['start'],
                        'end': ent['end']
                    })
            except Exception as e:
                print(f"NER pipeline error, using simple extraction: {e}")
                entities = self.simple_extraction(text)
        else:
            # Fallback to simple extraction
            entities = self.simple_extraction(text)
        
        # Deduplication
        seen = set()
        unique_entities = []
        for ent in entities:
            key = (ent['text'].lower(), ent['label'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)
        
        return unique_entities

if __name__ == "__main__":
    extractor = MedicalEntityExtractor()
    
    text = """
    Diabetes mellitus is characterized by hyperglycemia. 
    Treatment includes metformin and insulin therapy.
    Common symptoms include polyuria, polydipsia, and fatigue.
    Hypertension is a common comorbidity.
    """
    
    entities = extractor.extract_entities(text)
    print(f"\nExtracted {len(entities)} entities:")
    for ent in entities:
        print(f"  {ent['text']:20s} {ent['label']:15s} {ent['score']:.3f}")
