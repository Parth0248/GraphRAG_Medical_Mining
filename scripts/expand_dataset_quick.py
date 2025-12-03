"""Quick Dataset Expansion - Enhanced Sample Data Generator

Generates 300 detailed medical abstracts quickly without API calls.
For production, use fetch_pubmed_large.py to get real 1000+ PubMed abstracts.
"""

import json
from pathlib import Path
from datetime import datetime
import random

# Medical templates by category
TEMPLATES = {
    'diabetes': [
        "Type 2 diabetes mellitus is characterized by insulin resistance and hyperglycemia. First-line treatment includes metformin, which reduces hepatic glucose production. Patients present with polyuria, polydipsia, and unexplained weight loss. HbA1c levels above 6.5% confirm diagnosis. Lifestyle modifications including diet and exercise are essential. Complications include neuropathy, retinopathy, and cardiovascular disease.",
        "Gestational diabetes develops during pregnancy due to placental hormones. It increases risk of type 2 diabetes later in life. Treatment involves blood glucose monitoring and dietary management. Insulin therapy may be required if glycemic targets are not met. Regular prenatal care is crucial for maternal and fetal health.",
        "Type 1 diabetes is an autoimmune condition destroying pancreatic beta cells. It requires lifelong insulin therapy for survival. Patients typically present in childhood or adolescence with acute onset of symptoms. Continuous glucose monitoring improves glycemic control. Risk of diabetic ketoacidosis requires careful management."
    ],
    'hypertension': [
        "Essential hypertension affects millions worldwide, with blood pressure readings consistently above 140/90 mmHg. ACE inhibitors like lisinopril are first-line therapies. Lifestyle modifications include sodium restriction and regular aerobic exercise. Untreated hypertension increases risk of stroke and myocardial infarction. Home blood pressure monitoring improves treatment adherence.",
        "Secondary hypertension results from underlying conditions such as renal artery stenosis or pheochromocytoma. Treatment addresses the primary cause. Resistant hypertension requires combination therapy with multiple antihypertensive agents. Regular monitoring prevents target organ damage.",
        "Hypertensive emergency presents with severely elevated blood pressure and acute end-organ damage. Immediate treatment with IV nitroprusside or labetalol is required. Gradual blood pressure reduction prevents cerebrovascular complications. Close ICU monitoring is essential."
    ],
    'asthma': [
        "Asthma is a chronic inflammatory airway disease characterized by reversible bronchospasm. Inhaled corticosteroids are the cornerstone of long-term control. Albuterol provides rapid relief of acute symptoms. Peak flow monitoring helps assess disease control. Environmental trigger avoidance is crucial.",
        "Exercise-induced asthma occurs during or after physical activity. Pre-treatment with short-acting beta-agonists prevents symptoms. Proper warm-up and cool-down routines are beneficial. Chronic asthma management ensures participation in sports and activities.",
        "Severe asthma exacerbation requires emergency treatment with nebulized bronchodilators and systemic corticosteroids. Oxygen therapy maintains adequate saturation. Hospital admission may be necessary for severe cases. Patient education on proper inhaler technique prevents future exacerbations."
    ],
    'cardiovascular': [
        "Acute myocardial infarction presents with crushing chest pain, diaphoresis, and dyspnea. Immediate aspirin administration reduces mortality. Urgent cardiac catheterization enables percutaneous coronary intervention. Troponin elevation confirms myocardial damage. Secondary prevention includes statins and beta-blockers.",
        "Heart failure with reduced ejection fraction requires ACE inhibitors and beta-blockers. Diuretics relieve pulmonary congestion and peripheral edema. Device therapy including implantable defibrillators improves outcomes. Salt restriction and fluid monitoring are essential.",
        "Atrial fibrillation increases stroke risk fivefold. Anticoagulation with warfarin or DOACs prevents thromboembolic events. Rate control with beta-blockers or calcium channel blockers manages symptoms. Rhythm control through cardioversion or ablation may be considered."
    ],
    'respiratory': [
        "Chronic obstructive pulmonary disease results from long-term tobacco exposure. Spirometry demonstrates irreversible airflow obstruction. Long-acting bronchodilators improve symptoms and reduce exacerbations. Smoking cessation is the most effective intervention. Pulmonary rehabilitation enhances quality of life.",
        "Pneumonia presents with fever, productive cough, and pleuritic chest pain. Chest radiography reveals pulmonary infiltrates. Empiric antibiotic therapy with azithromycin or amoxicillin-clavulanate is initiated. Hospitalization criteria include hypoxemia and multilobar involvement.",
        "Pulmonary embolism causes acute dyspnea, chest pain, and hemoptysis. D-dimer elevation and CT angiography confirm diagnosis. Anticoagulation with heparin followed by warfarin or DOACs prevents recurrence. Thrombolysis may be required for massive PE."
    ],
    'neurology': [
        "Alzheimer disease is the most common cause of dementia, characterized by progressive memory loss and cognitive decline. Cholinesterase inhibitors like donepezil provide symptomatic improvement. Early diagnosis enables advance care planning. Caregiver support is essential for disease management.",
        "Parkinson disease features resting tremor, bradykinesia, and rigidity. Levodopa-carbidopa remains the gold standard treatment. Motor fluctuations and dyskinesias complicate long-term therapy. Deep brain stimulation benefits selected patients.",
        "Migraine headaches cause severe unilateral throbbing pain with photophobia and nausea. Triptans provide effective abortive treatment. Preventive therapy with beta-blockers or topiramate reduces attack frequency. Trigger identification and avoidance are important."
    ],
    'gastroenterology': [
        "Gastroesophageal reflux disease results from lower esophageal sphincter dysfunction. Proton pump inhibitors like omeprazole effectively reduce acid production. Lifestyle modifications include elevating the head of bed and avoiding trigger foods. Chronic GERD increases Barrett esophagus risk.",
        "Inflammatory bowel disease encompasses Crohn disease and ulcerative colitis. Immunosuppressive therapy with azathioprine or biologics induces remission. Colonoscopy with biopsy establishes diagnosis. Nutritional support is crucial during flares.",
        "Irritable bowel syndrome presents with abdominal pain and altered bowel habits. Treatment addresses predominant symptoms with antispasmodics or laxatives. Dietary modifications including low-FODMAP diet provide relief. Stress management improves outcomes."
    ],
    'rheumatology': [
        "Rheumatoid arthritis causes symmetric polyarthritis with morning stiffness exceeding one hour. Methotrexate is the anchor disease-modifying antirheumatic drug. Anti-CCP antibodies aid in diagnosis and prognosis. Early aggressive treatment prevents joint destruction.",
        "Systemic lupus erythematosus is a multisystem autoimmune disorder. Malar rash and photosensitivity are characteristic features. Hydroxychloroquine is used for mild disease. Severe manifestations require corticosteroids and immunosuppressants.",
        "Gout results from hyperuricemia and monosodium urate crystal deposition. Acute attacks present with severe joint pain and erythema. Colchicine or NSAIDs provide symptomatic relief. Allopurinol prevents recurrent attacks by lowering uric acid."
    ],
    'endocrine': [
        "Hypothyroidism causes fatigue, weight gain, and cold intolerance. TSH elevation with low free T4 confirms diagnosis. Levothyroxine replacement is standard treatment. Regular monitoring ensures adequate hormone levels. Hashimoto thyroiditis is the most common cause.",
        "Hyperthyroidism presents with weight loss, tremor, and heat intolerance. Graves disease accounts for most cases. Treatment options include antithyroid drugs, radioactive iodine ablation, or thyroidectomy. Beta-blockers manage sympathetic symptoms.",
        "Cushing syndrome results from chronic glucocorticoid excess. Central obesity, moon facies, and striae characterize the condition. Diagnosis involves 24-hour urinary cortisol measurement. Treatment addresses the underlying cause, often pituitary adenoma."
    ],
    'oncology': [
        "Non-small cell lung cancer is the leading cause of cancer death worldwide. Surgical resection offers cure for early-stage disease. Chemotherapy with platinum-based regimens treats advanced stages. Targeted therapy with EGFR inhibitors benefits mutation-positive patients.",
        "Breast cancer screening with mammography reduces mortality in women over 40. Treatment includes surgery, radiation, and systemic therapy. Hormone receptor-positive tumors respond to endocrine therapy. HER2-positive disease benefits from trastuzumab.",
        "Colorectal cancer screening beginning at age 45 detects precancerous polyps. Surgical resection is the primary treatment. Adjuvant chemotherapy improves survival in node-positive disease. Rising CEA levels suggest recurrence."
    ]
}

MEDICATIONS = {
    'diabetes': ['metformin', 'insulin', 'glipizide', 'sitagliptin', 'empagliflozin'],
    'hypertension': ['lisinopril', 'amlodipine', 'hydrochlorothiazide', 'losartan', 'metoprolol'],
    'asthma': ['albuterol', 'fluticasone', 'montelukast', 'budesonide', 'salmeterol'],
    'cardiovascular': ['aspirin', 'atorvastatin', 'clopidogrel', 'warfarin', 'metoprolol'],
    'respiratory': ['azithromycin', 'amoxicillin', 'prednisone', 'ipratropium', 'oxygen'],
    'neurology': ['levodopa', 'donepezil', 'sumatriptan', 'gabapentin', 'carbamazepine'],
    'gastroenterology': ['omeprazole', 'pantoprazole', 'mesalamine', 'azathioprine', 'loperamide'],
    'rheumatology': ['methotrexate', 'hydroxychloroquine', 'prednisone', 'colchicine', 'adalimumab'],
    'endocrine': ['levothyroxine', 'methimazole', 'radioactive iodine', 'hydrocortisone', 'fludrocortisone'],
    'oncology': ['cisplatin', 'carboplatin', 'paclitaxel', 'trastuzumab', 'pembrolizumab']
}

def generate_abstracts(total=100):
    """Generate medical abstracts"""
    abstracts = []
    pmid = 20001
    
    categories = list(TEMPLATES.keys())
    
    for i in range(total):
        category = random.choice(categories)
        template = random.choice(TEMPLATES[category])
        
        # Add category-specific medication
        medications = MEDICATIONS.get(category, [])
        if medications:
            med = random.choice(medications)
            template = template.replace(template.split('.')[0], f"{template.split('.')[0]}. Treatment with {med} has shown efficacy")
        
        abstracts.append({
            'pmid': str(pmid),
            'title': f"Clinical Management of {category.replace('_', ' ').title()} - Study {i+1}",
            'abstract': template,
            'year': str(random.choice([2022, 2023, 2024])),
            'category': category
        })
        pmid += 1
    
    return abstracts

def main():
    print("="*70)
    print("    Quick Dataset Expansion - Enhanced Sample Data")
    print("="*70)
    print("\n🚀 Generating 800 medical abstracts...")
    
    abstracts = generate_abstracts(800)
    
    # Save
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "pubmed_abstracts_expanded.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(abstracts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {len(abstracts)} abstracts")
    print(f"📁 Saved to: {output_file}")
    
    # Statistics
    print("\n📊 Category Distribution:")
    from collections import Counter
    categories = Counter([a['category'] for a in abstracts])
    for cat, count in sorted(categories.items()):
        print(f"   {cat:20s}: {count:3d} abstracts")
    
    print("\n" + "="*70)
    print("✅ Dataset expansion complete!")
    print("="*70)
    print("\n📌 Next step:")
    print("   Run: python src/graph_construction/build_graph.py")
    print("   This will populate Neo4j with ~1000+ nodes")
    print("="*70)

if __name__ == "__main__":
    main()
