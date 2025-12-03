"""Advanced Medical Features for GraphRAG System

1. Drug-Drug Interaction Checker
2. Differential Diagnosis Assistant  
3. Medical Knowledge Graph Reasoning
"""

from neo4j import GraphDatabase
from typing import List, Dict, Set, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


class DrugInteractionChecker:
    """Check for drug-drug interactions"""
    
    def __init__(self, uri, username, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def check_interactions(self, medications: List[str]) -> List[Dict]:
        """
        Check for interactions between medications
        
        Args:
            medications: List of medication names
            
        Returns:
            List of interactions with severity and description
        """
        interactions = []
        
        with self.driver.session() as session:
            for i, med1 in enumerate(medications):
                for med2 in medications[i+1:]:
                    # Query for CONTRAINDICATES relationship
                    result = session.run(
                        """
                        MATCH (d1:Drug {name: $med1})-[r:CONTRAINDICATES]-(d2:Drug {name: $med2})
                        RETURN r.severity as severity, r.description as description, r.mechanism as mechanism
                        UNION
                        MATCH (d1:Medication {name: $med1})-[r:CONTRAINDICATES]-(d2:Medication {name: $med2})
                        RETURN r.severity as severity, r.description as description, r.mechanism as mechanism
                        """,
                        med1=med1, med2=med2
                    )
                    
                    for record in result:
                        interactions.append({
                            'drug1': med1,
                            'drug2': med2,
                            'severity': record.get('severity', 'Unknown'),
                            'description': record.get('description', 'Interaction detected'),
                            'mechanism': record.get('mechanism', 'Not specified')
                        })
        
        return interactions
    
    def close(self):
        """Close connection"""
        self.driver.close()


class DifferentialDiagnosisAssistant:
    """Suggest possible diagnoses based on symptoms"""
    
    def __init__(self, uri, username, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def suggest_diagnoses(self, symptoms: List[str], top_k: int = 5) -> List[Dict]:
        """
        Suggest possible diagnoses based on symptom list
        
        Args:
            symptoms: List of symptom names
            top_k: Number of top diagnoses to return
            
        Returns:
            List of possible diagnoses with confidence scores
        """
        with self.driver.session() as session:
            # Find diseases that match the symptoms
            result = session.run(
                """
                MATCH (s:Symptom)-[:SYMPTOM_OF]-(d:Disease)
                WHERE toLower(s.name) IN $symptoms
                WITH d, count(s) as matching_symptoms
                MATCH (d)-[:HAS_SYMPTOM]-(all_symptoms:Symptom)
                WITH d, matching_symptoms, count(DISTINCT all_symptoms) as total_symptoms
                RETURN d.name as disease,
                       matching_symptoms,
                       total_symptoms,
                       toFloat(matching_symptoms) / total_symptoms as confidence
                ORDER BY confidence DESC, matching_symptoms DESC
                LIMIT $top_k
                UNION
                MATCH (s:Sign_symptom)-[:MENTIONED_IN]->(doc:Document)<-[:MENTIONED_IN]-(d:Disease_disorder)
                WHERE toLower(s.name) IN $symptoms
                WITH d, count(DISTINCT s) as matching_symptoms
                RETURN d.name as disease,
                       matching_symptoms,
                       matching_symptoms as total_symptoms,
                       toFloat(matching_symptoms) / (matching_symptoms + 1.0) as confidence
                ORDER BY confidence DESC, matching_symptoms DESC
                LIMIT $top_k
                """,
                symptoms=[s.lower() for s in symptoms],
                top_k=top_k
            )
            
            diagnoses = []
            for record in result:
                diagnoses.append({
                    'disease': record['disease'],
                    'matching_symptoms': record['matching_symptoms'],
                    'total_symptoms': record['total_symptoms'],
                    'confidence': record['confidence'],
                    'match_percentage': f"{record['confidence'] * 100:.1f}%"
                })
            
            return diagnoses
    
    def get_additional_symptoms(self, disease: str) -> List[str]:
        """Get additional symptoms to ask about for a disease"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Disease {name: $disease})-[:HAS_SYMPTOM]-(s:Symptom)
                RETURN s.name as symptom
                LIMIT 10
                UNION
                MATCH (d:Disease_disorder {name: $disease})-[:MENTIONED_IN]->(doc:Document)<-[:MENTIONED_IN]-(s:Sign_symptom)
                RETURN DISTINCT s.name as symptom
                LIMIT 10
                """,
                disease=disease
            )
            
            return [record['symptom'] for record in result]
    
    def close(self):
        """Close connection"""
        self.driver.close()


class MedicalKnowledgeReasoner:
    """Complex reasoning queries on medical knowledge graph"""
    
    def __init__(self, uri, username, password):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def find_treatment_alternatives(self, disease: str, exclude_drugs: List[str] = None) -> List[Dict]:
        """
        Find alternative treatments for a disease
        
        Args:
            disease: Disease name
            exclude_drugs: Drugs to exclude (e.g., due to allergies)
            
        Returns:
            List of alternative treatments
        """
        exclude_drugs = exclude_drugs or []
        
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (disease:Disease {name: $disease})-[r:TREATED_BY]-(drug:Drug)
                WHERE NOT drug.name IN $exclude_drugs
                RETURN drug.name as treatment,
                       r.efficacy as efficacy,
                       r.common_dosage as dosage
                ORDER BY r.efficacy DESC
                UNION
                MATCH (disease:Disease_disorder {name: $disease})-[:MENTIONED_IN]->(doc:Document)<-[:MENTIONED_IN]-(med:Medication)
                WHERE NOT med.name IN $exclude_drugs
                RETURN DISTINCT med.name as treatment,
                       null as efficacy,
                       null as dosage
                """,
                disease=disease,
                exclude_drugs=exclude_drugs
            )
            
            treatments = []
            for record in result:
                treatments.append({
                    'treatment': record['treatment'],
                    'efficacy': record.get('efficacy'),
                    'dosage': record.get('dosage')
                })
            
            return treatments
    
    def find_related_conditions(self, disease: str, max_depth: int = 2) -> List[Tuple[str, str]]:
        """
        Find conditions related to a disease through comorbidity or shared symptoms
        
        Args:
            disease: Disease name
            max_depth: Maximum relationship depth
            
        Returns:
            List of (related_disease, relationship_path) tuples
        """
        with self.driver.session() as session:
            # Use f-string for max_depth since it can't be parameterized in relationship pattern
            query = f"""
                MATCH path = (d1:Disease {{name: $disease}})-[*1..{max_depth}]-(d2:Disease)
                WHERE d1 <> d2
                RETURN DISTINCT d2.name as related_disease,
                       [rel in relationships(path) | type(rel)] as path_types
                LIMIT 20
                """
            
            result = session.run(query, disease=disease)
            
            related = []
            for record in result:
                related.append((
                    record['related_disease'],
                    ' → '.join(record['path_types'])
                ))
            
            return related
    
    def find_drugs_without_interaction(self, existing_medications: List[str], 
                                       target_disease: str) -> List[str]:
        """
        Find drugs that treat a disease and don't interact with existing medications
        
        Args:
            existing_medications: Current medications
            target_disease: Disease to treat
            
        Returns:
            List of safe medication options
        """
        with self.driver.session() as session:
            # This is a simplified version
            # In practice, would need full drug interaction database
            result = session.run(
                """
                MATCH (disease:Disease {name: $disease})-[:TREATED_BY]-(drug:Drug)
                WHERE NOT EXISTS {
                    MATCH (drug)-[:CONTRAINDICATES]-(other:Drug)
                    WHERE other.name IN $existing_meds
                }
                RETURN drug.name as safe_drug
                """,
                disease=target_disease,
                existing_meds=existing_medications
            )
            
            return [record['safe_drug'] for record in result]
    
    def close(self):
        """Close connection"""
        self.driver.close()


# Demo functions
def demo_drug_interaction():
    """Demo drug interaction checker"""
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    
    print("\n" + "="*70)
    print("       Drug-Drug Interaction Checker Demo")
    print("="*70)
    
    checker = DrugInteractionChecker(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    medications = ["aspirin", "warfarin", "metformin"]
    print(f"\nChecking interactions for: {', '.join(medications)}")
    
    interactions = checker.check_interactions(medications)
    
    if interactions:
        print(f"\n⚠️  Found {len(interactions)} interaction(s):")
        for interaction in interactions:
            print(f"\n   {interaction['drug1']} + {interaction['drug2']}")
            print(f"   Severity: {interaction['severity']}")
            print(f"   Description: {interaction['description']}")
    else:
        print("\n✅ No interactions found")
    
    checker.close()


def demo_differential_diagnosis():
    """Demo differential diagnosis assistant"""
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    
    print("\n" + "="*70)
    print("       Differential Diagnosis Assistant Demo")
    print("="*70)
    
    assistant = DifferentialDiagnosisAssistant(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    symptoms = ["headache", "fever", "cough"]
    print(f"\nPatient symptoms: {', '.join(symptoms)}")
    
    diagnoses = assistant.suggest_diagnoses(symptoms, top_k=5)
    
    if diagnoses:
        print(f"\n🩺 Top {len(diagnoses)} possible diagnoses:")
        for i, diagnosis in enumerate(diagnoses, 1):
            print(f"\n   {i}. {diagnosis['disease']}")
            print(f"      Confidence: {diagnosis['match_percentage']}")
            print(f"      Matching symptoms: {diagnosis['matching_symptoms']}/{diagnosis['total_symptoms']}")
    else:
        print("\n⚠️  No matching diagnoses found")
    
    assistant.close()


def demo_knowledge_reasoning():
    """Demo knowledge graph reasoning"""
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    
    print("\n" + "="*70)
    print("       Medical Knowledge Graph Reasoning Demo")
    print("="*70)
    
    reasoner = MedicalKnowledgeReasoner(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    disease = "diabetes"
    print(f"\nFinding treatment alternatives for: {disease}")
    
    treatments = reasoner.find_treatment_alternatives(disease)
    
    if treatments:
        print(f"\n💊 Found {len(treatments)} treatment option(s):")
        for treatment in treatments[:5]:
            print(f"   - {treatment['treatment']}")
            if treatment.get('efficacy'):
                print(f"     Efficacy: {treatment['efficacy']}")
    else:
        print("\n⚠️  No treatments found")
    
    # Find related conditions
    print(f"\n\nFinding conditions related to: {disease}")
    related = reasoner.find_related_conditions(disease)
    
    if related:
        print(f"\n🔗 Found {len(related)} related condition(s):")
        for condition, path in related[:5]:
            print(f"   - {condition}")
            print(f"     Connection: {path}")
    
    reasoner.close()


if __name__ == "__main__":
    print("="*70)
    print("       Advanced Medical Features - Demo")
    print("="*70)
    
    # Run demos
    demo_drug_interaction()
    demo_differential_diagnosis()
    demo_knowledge_reasoning()
    
    print("\n" + "="*70)
    print("✅ All demos complete!")
    print("="*70)
