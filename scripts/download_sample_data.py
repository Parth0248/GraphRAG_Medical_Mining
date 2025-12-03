"""Enhanced sample medical data generator"""
import json
from pathlib import Path
import pandas as pd

def create_enhanced_sample_data():
    """Create comprehensive sample medical data for demo"""
    
    # Create directories
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Enhanced PubMed abstracts with more medical content
    sample_abstracts = [
        {
            'pmid': '10001',
            'title': 'Management of Type 2 Diabetes Mellitus',
            'abstract': '''Metformin is recommended as first-line pharmacological therapy for type 2 diabetes mellitus. 
            Patients typically present with polyuria, polydipsia, and unexplained weight loss. Blood glucose levels above 126 mg/dL 
            indicate diabetes. Metformin reduces hepatic glucose production and improves insulin sensitivity. Common side effects 
            include nausea and diarrhea. Alternative treatments include sulfonylureas and insulin therapy.''',
            'year': '2023'
        },
        {
            'pmid': '10002',
            'title': 'Hypertension: Guidelines and Treatment Strategies',
            'abstract': '''Hypertension affects approximately 30% of adults worldwide. Blood pressure readings above 140/90 mmHg 
            warrant treatment. First-line therapies include ACE inhibitors like lisinopril and ARBs. Calcium channel blockers 
            and thiazide diuretics are also effective. Patients may experience headaches, dizziness, and blurred vision. 
            Lifestyle modifications include reduced sodium intake and regular exercise.''',
            'year': '2023'
        },
        {
            'pmid': '10003',
            'title': 'Asthma Pathophysiology and Current Treatments',
            'abstract': '''Asthma is characterized by airway inflammation and bronchospasm. Common symptoms include wheezing, 
            shortness of breath, and chest tightness. Albuterol is a short-acting beta-agonist used for acute symptoms. 
            Inhaled corticosteroids provide long-term control. Environmental triggers include allergens, cold air, and exercise. 
            Peak flow monitoring helps assess asthma control.''',
            'year': '2024'
        },
        {
            'pmid': '10004',
            'title': 'Cardiovascular Disease Prevention',
            'abstract': '''Cardiovascular disease remains the leading cause of mortality globally. Risk factors include 
            hypertension, diabetes, smoking, and hyperlipidemia. Aspirin provides antiplatelet effects for secondary prevention. 
            Statins like atorvastatin reduce LDL cholesterol. Symptoms of myocardial infarction include chest pain, dyspnea, 
            and diaphoresis. Emergency treatment involves aspirin, nitroglycerin, and urgent cardiac catheterization.''',
            'year': '2023'
        },
        {
            'pmid': '10005',
            'title': 'Depression and Anxiety Disorders',
            'abstract': '''Major depressive disorder affects millions worldwide. Symptoms include persistent sadness, anhedonia, 
            and sleep disturbances. First-line treatments are SSRIs like sertraline and fluoxetine. Cognitive behavioral therapy 
            shows efficacy comparable to medication. Generalized anxiety disorder presents with excessive worry and restlessness. 
            Benzodiazepines provide short-term anxiety relief but carry addiction risk.''',
            'year': '2024'
        },
        {
            'pmid': '10006',
            'title': 'Chronic Obstructive Pulmonary Disease Management',
            'abstract': '''COPD is primarily caused by cigarette smoking. Patients present with chronic cough, sputum production, 
            and progressive dyspnea. Spirometry shows irreversible airflow obstruction. Long-acting bronchodilators improve symptoms. 
            Inhaled corticosteroids reduce exacerbation frequency. Smoking cessation is the most effective intervention. 
            Oxygen therapy benefits patients with severe hypoxemia.''',
            'year': '2023'
        },
        {
            'pmid': '10007',
            'title': 'Rheumatoid Arthritis: Diagnosis and Treatment',
            'abstract': '''Rheumatoid arthritis is an autoimmune disease causing joint inflammation. Patients experience morning 
            stiffness, joint swelling, and pain. Rheumatoid factor and anti-CCP antibodies aid diagnosis. Methotrexate is the 
            anchor drug for treatment. Biologic agents like TNF inhibitors show excellent efficacy. NSAIDs like ibuprofen provide 
            symptomatic relief. Early aggressive treatment prevents joint destruction.''',
            'year': '2024'
        },
        {
            'pmid': '10008',
            'title': 'Migraine Headache: Pathophysiology and Management',
            'abstract': '''Migraine is a neurovascular disorder causing severe headache. Symptoms include unilateral throbbing pain, 
            photophobia, and nausea. Triptans like sumatriptan are effective abortive treatments. Preventive medications include 
            beta-blockers and topiramate. Aura may precede headache onset. Triggers include stress, certain foods, and hormonal 
            changes. Chronic migraine may require CGRP antagonists.''',
            'year': '2023'
        },
        {
            'pmid': '10009',
            'title': 'Gastroesophageal Reflux Disease Treatment',
            'abstract': '''GERD results from lower esophageal sphincter dysfunction. Patients report heartburn, regurgitation, 
            and dysphagia. Proton pump inhibitors like omeprazole effectively reduce acid production. H2 blockers provide 
            alternative therapy. Lifestyle modifications include elevating the head of bed and avoiding trigger foods. 
            Chronic GERD increases risk of Barrett\'s esophagus.''',
            'year': '2024'
        },
        {
            'pmid': '10010',
            'title': 'Hypothyroidism: Clinical Features and Treatment',
            'abstract': '''Hypothyroidism results from insufficient thyroid hormone production. Common symptoms include fatigue, 
            weight gain, cold intolerance, and constipation. TSH elevation confirms diagnosis. Levothyroxine replacement is 
            standard treatment. Hashimoto\'s thyroiditis is the most common cause. Monitoring TSH levels ensures adequate 
            replacement. Untreated hypothyroidism may cause myxedema coma.''',
            'year': '2023'
        }
    ]
    
    # Save abstracts
    with open("data/raw/pubmed_abstracts.json", 'w') as f:
        json.dump(sample_abstracts, f, indent=2)
    
    # Disease-symptom relationships
    disease_symptom_data = {
        'Disease': [
            'Diabetes', 'Hypertension', 'Asthma', 'Depression', 'COPD',
            'Rheumatoid Arthritis', 'Migraine', 'GERD', 'Hypothyroidism', 'CVD'
        ],
        'Symptom_1': [
            'polyuria', 'headache', 'wheezing', 'sadness', 'cough',
            'joint pain', 'headache', 'heartburn', 'fatigue', 'chest pain'
        ],
        'Symptom_2': [
            'polydipsia', 'dizziness', 'shortness of breath', 'anhedonia', 'dyspnea',
            'stiffness', 'photophobia', 'regurgitation', 'weight gain', 'dyspnea'
        ],
        'Symptom_3': [
            'weight loss', 'blurred vision', 'chest tightness', 'fatigue', 'sputum',
            'swelling', 'nausea', 'dysphagia', 'cold intolerance', 'diaphoresis'
        ],
        'Treatment': [
            'metformin', 'lisinopril', 'albutol', 'sertraline', 'bronchodilators',
            'methotrexate', 'sumatriptan', 'omeprazole', 'levothyroxine', 'aspirin'
        ]
    }
    
    df = pd.DataFrame(disease_symptom_data)
    df.to_csv("data/raw/disease_symptom.csv", index=False)
    
    print("✅ Enhanced sample data created")
    print(f"   - {len(sample_abstracts)} PubMed abstracts")
    print(f"   - {len(disease_symptom_data['Disease'])} disease-symptom pairs")
    print("\nFiles created:")
    print("  📄 data/raw/pubmed_abstracts.json")
    print("  📄 data/raw/disease_symptom.csv")

if __name__ == "__main__":
    create_enhanced_sample_data()
