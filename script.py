import pandas as pd
import json

# Create enhanced symptom-disease-medication mapping dataset
enhanced_medical_data = [
    {
        "symptom": "headache",
        "disease": "Tension Headache",
        "severity": "Mild to Moderate",
        "description": "A common type of headache characterized by a dull, aching sensation all over the head. Often described as feeling like a tight band around the head.",
        "medication": "Ibuprofen 400mg, Paracetamol 500mg, Aspirin 325mg",
        "precautions": "Stay hydrated, get adequate sleep, manage stress, avoid loud noises, rest in a dark room",
        "treatment": "Apply cold or warm compress, gentle massage, relaxation techniques",
        "diet": "Stay hydrated, avoid alcohol, limit caffeine, eat regular meals",
        "when_to_see_doctor": "If headaches are frequent, severe, or accompanied by fever, confusion, or vision changes"
    },
    {
        "symptom": "fever",
        "disease": "Viral Fever",
        "severity": "Mild to High",
        "description": "An elevation in body temperature often indicating the body's immune response to infection.",
        "medication": "Paracetamol 500mg (every 6-8 hours), Ibuprofen 400mg (every 8 hours), Aspirin 325mg (for adults only)",
        "precautions": "Rest, stay hydrated, monitor temperature, wear light clothing, take lukewarm baths",
        "treatment": "Plenty of fluids, rest, cool compresses, fever-reducing medications",
        "diet": "Light foods, broths, fruits, plenty of water, avoid heavy meals",
        "when_to_see_doctor": "If fever exceeds 103°F (39.4°C), persists for more than 3 days, or if breathing difficulties occur"
    },
    {
        "symptom": "cough",
        "disease": "Dry Cough",
        "severity": "Mild to Moderate",
        "description": "A persistent cough without phlegm production, often caused by irritation in the throat or airways.",
        "medication": "Dextromethorphan 15mg, Honey-based cough syrups, Throat lozenges with menthol",
        "precautions": "Stay hydrated, avoid irritants like smoke, use humidifier, avoid cold drinks",
        "treatment": "Warm salt water gargles, honey with warm water, steam inhalation",
        "diet": "Warm liquids, honey, ginger tea, avoid cold and spicy foods",
        "when_to_see_doctor": "If cough persists for more than 2 weeks, accompanied by blood, or severe chest pain"
    },
    {
        "symptom": "sore throat",
        "disease": "Pharyngitis",
        "severity": "Mild to Moderate", 
        "description": "Inflammation of the pharynx causing pain, scratchiness, or irritation of the throat.",
        "medication": "Throat lozenges, Benzocaine throat sprays, Ibuprofen 400mg, Paracetamol 500mg",
        "precautions": "Gargle with warm salt water, stay hydrated, avoid shouting, rest voice",
        "treatment": "Warm salt water gargles, throat sprays, pain relievers, rest",
        "diet": "Warm liquids, soft foods, honey, avoid spicy and acidic foods",
        "when_to_see_doctor": "If accompanied by high fever, difficulty swallowing, or white patches on throat"
    },
    {
        "symptom": "stomach pain",
        "disease": "Gastritis",
        "severity": "Mild to Moderate",
        "description": "Inflammation of the stomach lining causing pain, bloating, and digestive discomfort.",
        "medication": "Antacids (Calcium carbonate 500mg), Ranitidine 150mg, Omeprazole 20mg",
        "precautions": "Eat small frequent meals, avoid spicy foods, manage stress, don't lie down after eating",
        "treatment": "Dietary modifications, stress management, avoid NSAIDs, proper meal timing",
        "diet": "Bland foods, avoid spicy/acidic foods, small frequent meals, bananas, rice",
        "when_to_see_doctor": "If pain is severe, persistent, or accompanied by vomiting blood"
    },
    {
        "symptom": "cold",
        "disease": "Common Cold",
        "severity": "Mild",
        "description": "A viral infection of the upper respiratory tract causing congestion, runny nose, and mild discomfort.",
        "medication": "Decongestants (Pseudoephedrine 30mg), Antihistamines (Cetirizine 10mg), Paracetamol 500mg",
        "precautions": "Rest, stay hydrated, wash hands frequently, avoid close contact with others",
        "treatment": "Rest, fluids, nasal decongestants, steam inhalation",
        "diet": "Warm liquids, soups, vitamin C rich foods, honey, ginger tea",
        "when_to_see_doctor": "If symptoms worsen after 7 days or accompanied by high fever"
    },
    {
        "symptom": "diarrhea",
        "disease": "Acute Diarrhea",
        "severity": "Mild to Moderate",
        "description": "Frequent loose or watery bowel movements, often due to infection or dietary issues.",
        "medication": "Loperamide 2mg, ORS packets, Probiotics, Zinc supplements 20mg",
        "precautions": "Stay hydrated, wash hands frequently, avoid dairy, rest",
        "treatment": "Oral rehydration solution, BRAT diet, rest, avoid anti-diarrheal if fever present",
        "diet": "BRAT diet (Bananas, Rice, Applesauce, Toast), clear fluids, avoid dairy and fatty foods",
        "when_to_see_doctor": "If severe dehydration, blood in stool, or high fever occurs"
    },
    {
        "symptom": "nausea",
        "disease": "Gastroenteritis",
        "severity": "Mild to Moderate",
        "description": "A feeling of sickness with an inclination to vomit, often accompanied by stomach discomfort.",
        "medication": "Ondansetron 4mg, Domperidone 10mg, Ginger supplements 250mg",
        "precautions": "Eat small frequent meals, avoid strong odors, stay hydrated, rest",
        "treatment": "Small sips of clear fluids, ginger tea, rest, avoid solid foods initially",
        "diet": "Clear liquids, crackers, toast, bananas, avoid fatty and spicy foods",
        "when_to_see_doctor": "If accompanied by severe dehydration, high fever, or persistent vomiting"
    },
    {
        "symptom": "back pain",
        "disease": "Lower Back Strain",
        "severity": "Mild to Moderate",
        "description": "Pain in the lower back region, often due to muscle strain or poor posture.",
        "medication": "Ibuprofen 400mg, Diclofenac gel (topical), Muscle relaxants (Cyclobenzaprine 5mg)",
        "precautions": "Maintain good posture, avoid heavy lifting, use proper lifting techniques, apply heat/cold",
        "treatment": "Rest, ice/heat therapy, gentle stretching, physical therapy exercises",
        "diet": "Anti-inflammatory foods, adequate calcium and vitamin D, stay hydrated",
        "when_to_see_doctor": "If pain radiates to legs, numbness occurs, or doesn't improve in 2 weeks"
    },
    {
        "symptom": "joint pain",
        "disease": "Arthritis",
        "severity": "Moderate to High",
        "description": "Pain, stiffness, and inflammation in one or more joints, affecting mobility and daily activities.",
        "medication": "Ibuprofen 400mg, Diclofenac 50mg, Topical pain relievers (Capsaicin cream)",
        "precautions": "Gentle exercise, maintain healthy weight, protect joints, use assistive devices",
        "treatment": "Physical therapy, heat/cold therapy, gentle exercise, weight management",
        "diet": "Anti-inflammatory foods, omega-3 fatty acids, avoid processed foods",
        "when_to_see_doctor": "If joint becomes severely swollen, red, warm, or movement is significantly limited"
    },
    {
        "symptom": "shortness of breath",
        "disease": "Bronchial Asthma",
        "severity": "Mild to Severe",
        "description": "A chronic inflammatory disease of the airways leading to wheezing, breathlessness, and coughing.",
        "medication": "Salbutamol inhaler 100mcg, Montelukast 10mg",
        "precautions": "Avoid known triggers, carry inhaler, monitor peak flow",
        "treatment": "Inhaled bronchodilators, steam inhalation, upright rest",
        "diet": "Avoid cold drinks, eat small meals",
        "when_to_see_doctor": "If breathing worsens, lips or face turn blue, or peak flow falls dangerously low"
    },
    {
        "symptom": "runny nose",
        "disease": "Allergic Rhinitis",
        "severity": "Mild",
        "description": "Clear nasal discharge triggered by allergens such as dust, pollen, or animals.",
        "medication": "Antihistamines (Loratadine 10mg), Nasal saline spray",
        "precautions": "Avoid allergens, keep indoor air clean",
        "treatment": "Allergen avoidance, antihistamines, nasal irrigation",
        "diet": "Plenty of fluids, vitamin C foods",
        "when_to_see_doctor": "If severe congestion, facial pain, or lasts beyond 14 days"
    },
    {
        "symptom": "dizziness",
        "disease": "Vertigo",
        "severity": "Mild to Moderate",
        "description": "A sensation of spinning, often due to issues in the inner ear.",
        "medication": "Betahistine 16mg, Meclizine 25mg",
        "precautions": "Avoid sudden head movements, sit or lie down immediately",
        "treatment": "Vestibular exercises, hydration, rest",
        "diet": "Stay hydrated, avoid caffeine and alcohol",
        "when_to_see_doctor": "If accompanied by fainting, vision changes, or weakness"
    },
    {
        "symptom": "itchy skin",
        "disease": "Dermatitis",
        "severity": "Mild to Moderate",
        "description": "Red, itchy, and inflamed skin triggered by allergies or irritants.",
        "medication": "Hydrocortisone cream, Cetirizine 10mg, Calamine lotion",
        "precautions": "Avoid scratching, use gentle cleansers, moisturize",
        "treatment": "Topical steroids, antihistamines, avoid triggers",
        "diet": "Omega-3 rich foods, avoid allergens",
        "when_to_see_doctor": "If severe rash, pus, or fever develop"
    },
    {
        "symptom": "numbness in hand",
        "disease": "Carpal Tunnel Syndrome",
        "severity": "Mild to Moderate",
        "description": "Pressure on the median nerve in the wrist leading to numbness and tingling in the hand.",
        "medication": "NSAIDs, vitamin B6 supplements",
        "precautions": "Take breaks from repetitive wrist work, use wrist splints",
        "treatment": "Wrist splints, ergonomic adjustments, stretching",
        "diet": "B vitamins, lean proteins",
        "when_to_see_doctor": "If numbness spreads or hand weakness occurs"
    },
    {
        "symptom": "watery eyes",
        "disease": "Conjunctivitis",
        "severity": "Mild to Moderate",
        "description": "Inflammation or infection of the eye's conjunctiva causing redness, watering, and irritation.",
        "medication": "Lubricant eye drops, Antihistamine drops, Antibiotic drops (as prescribed)",
        "precautions": "Avoid touching eyes, use clean cloth, wash hands",
        "treatment": "Cool compress, eye drops, avoid contact lenses",
        "diet": "Hydration, vitamin A rich foods",
        "when_to_see_doctor": "If vision changes, severe pain, or thick pus appear"
    },
    {
        "symptom": "swollen ankle",
        "disease": "Ankle Sprain",
        "severity": "Mild to Moderate",
        "description": "Injury to ligaments around the ankle joint, leading to swelling and pain.",
        "medication": "Ibuprofen 400mg, Paracetamol 500mg",
        "precautions": "Rest, avoid putting weight, use compression bandage",
        "treatment": "RICE protocol: Rest, Ice, Compression, Elevation",
        "diet": "Protein-rich foods for healing, hydration",
        "when_to_see_doctor": "If unable to walk or severe deformity"
    },
    {
        "symptom": "blurred vision",
        "disease": "Refractive Error",
        "severity": "Mild to Moderate",
        "description": "Difficulty seeing clearly due to common vision problems such as myopia, hyperopia, or astigmatism.",
        "medication": "No medication—corrective glasses or contact lenses",
        "precautions": "Limit screen time, take eye breaks",
        "treatment": "Eye exam, prescription lenses, proper lighting",
        "diet": "Vitamin A, leafy greens, fish oils",
        "when_to_see_doctor": "If sudden vision loss, double vision, or pain"
    },
    {
        "symptom": "frequent urination",
        "disease": "Urinary Tract Infection (UTI)",
        "severity": "Mild to Moderate",
        "description": "Burning, urgency, and increased frequency of urination due to bacterial infection.",
        "medication": "Nitrofurantoin 100mg, Cranberry extract supplements, Paracetamol for pain",
        "precautions": "Maintain hygiene, urinate after intercourse, drink fluids",
        "treatment": "Antibiotics (doctor prescribed), hydration, avoid irritants",
        "diet": "Plenty of fluids, cranberry juice, avoid caffeine",
        "when_to_see_doctor": "If fever, back pain, or blood in urine"
    },
    {
        "symptom": "weight loss",
        "disease": "Hyperthyroidism",
        "severity": "Mild to Moderate",
        "description": "Unintentional weight loss, increased appetite, and sweating due to thyroid gland overactivity.",
        "medication": "Methimazole 10mg, Beta-blockers (Propranolol 20mg)",
        "precautions": "Monitor heart rate, avoid stimulants, regular thyroid checks",
        "treatment": "Thyroid medications, diet monitoring",
        "diet": "Balanced diet, calcium and vitamin D, avoid excess iodine",
        "when_to_see_doctor": "If rapid heartbeat, severe weakness"
    },
    {
        "symptom": "muscle cramps",
        "disease": "Muscle Spasm",
        "severity": "Mild",
        "description": "Involuntary contraction of a muscle, often occurring after exercise or dehydration.",
        "medication": "Magnesium supplements, Ibuprofen 400mg",
        "precautions": "Stretch before activity, stay hydrated",
        "treatment": "Gentle stretching, massage",
        "diet": "Bananas, leafy greens, hydration",
        "when_to_see_doctor": "If persistent or associated with numbness"
    },
    {
        "symptom": "nosebleed",
        "disease": "Epistaxis",
        "severity": "Mild to Moderate",
        "description": "Bleeding from the nasal cavity, often due to dry air, trauma, or allergies.",
        "medication": "Oxymetazoline nasal spray, Saline nasal drops",
        "precautions": "Avoid nose picking/blowing, humidify air",
        "treatment": "Pinch nostrils, lean forward, cold compress",
        "diet": "Hydration, vitamin C rich foods",
        "when_to_see_doctor": "If bleeding >20 min or frequent recurrences"
    },
    {
        "symptom": "ringing in ears",
        "disease": "Tinnitus",
        "severity": "Mild to Moderate",
        "description": "A ringing, buzzing or hissing sound in the ears with no external source.",
        "medication": "No direct medication for most cases, treat underlying cause",
        "precautions": "Avoid loud noise, manage stress",
        "treatment": "Sound therapy, tinnitus retraining, relaxation",
        "diet": "Reduce caffeine & salt",
        "when_to_see_doctor": "If persistent or associated with hearing loss"
    },
    {
        "symptom": "night sweats",
        "disease": "Tuberculosis (early), or Menopause",
        "severity": "Mild to Severe",
        "description": "Excessive sweating during sleep, can be related to infection, menopause, or lymphoma.",
        "medication": "As per diagnosis: hormone therapy, anti-TB drugs (doctor prescribed)",
        "precautions": "Monitor for unexplained fever or weight loss",
        "treatment": "Address underlying cause",
        "diet": "Nutritious, balanced",
        "when_to_see_doctor": "If persistent with fever and cough"
    },
    {
        "symptom": "vomiting",
        "disease": "Viral Gastroenteritis",
        "severity": "Mild",
        "description": "Forceful expulsion of stomach contents through the mouth, often from stomach infection.",
        "medication": "Ondansetron 4mg, Oral rehydration salts",
        "precautions": "Sip fluids slowly, rest",
        "treatment": "Rehydration, light diet",
        "diet": "Clear liquids, crackers",
        "when_to_see_doctor": "If unable to keep fluids down"
    },
    {
        "symptom": "heartburn",
        "disease": "Acid Reflux (GERD)",
        "severity": "Mild to Moderate",
        "description": "Burning sensation in chest, usually after eating, due to stomach acid moving up esophagus.",
        "medication": "Antacids, Omeprazole 20mg, Ranitidine 150mg",
        "precautions": "Avoid spicy/fatty foods, don’t lie down after eating",
        "treatment": "Meal timing, dietary changes, weight management",
        "diet": "Bland foods, avoid caffeinated/drinks",
        "when_to_see_doctor": "If daily or severe symptoms"
    },
    {
        "symptom": "palpitations",
        "disease": "Anxiety Attack",
        "severity": "Mild to Moderate",
        "description": "Feeling like the heart is racing, pounding, or skipping beats, often due to stress or panic.",
        "medication": "Short-term: Propranolol 10mg, manage anxiety",
        "precautions": "Avoid stimulants, practice relaxation",
        "treatment": "Deep breathing, mindfulness",
        "diet": "Avoid caffeine, sugary drinks",
        "when_to_see_doctor": "If fainting, chest pain, or shortness of breath"
    },
    {
        "symptom": "rash",
        "disease": "Allergic Dermatitis",
        "severity": "Mild to Moderate",
        "description": "Red, itchy, possibly raised patches of skin in response to allergens.",
        "medication": "Antihistamines (Cetirizine 10mg), Hydrocortisone cream",
        "precautions": "Identify and avoid triggers",
        "treatment": "Soothing lotions, cool compress",
        "diet": "Avoid known food allergens",
        "when_to_see_doctor": "If swelling, blistering, or signs of infection"
    },
    {
        "symptom": "loss of appetite",
        "disease": "Gastric Ulcer",
        "severity": "Mild to Moderate",
        "description": "Decreased interest in eating, sometimes with stomach pain, often due to ulcers or infection.",
        "medication": "Omeprazole 20mg, Sucralfate, Antibiotics (H. pylori)",
        "precautions": "Avoid irritant foods, small frequent meals",
        "treatment": "Antacids, treat underlying cause",
        "diet": "Bland, frequent meals",
        "when_to_see_doctor": "If persistent >5 days or weight loss"
    },
    {
        "symptom": "foot pain",
        "disease": "Plantar Fasciitis",
        "severity": "Mild to Moderate",
        "description": "Heel or arch pain, worse on first steps in the morning.",
        "medication": "NSAIDs, Orthotic insoles",
        "precautions": "Stretch calves, wear supportive shoes",
        "treatment": "Rest, ice, foot stretches",
        "diet": "Calcium, Vitamin D",
        "when_to_see_doctor": "If not improving after 2 weeks"
    },
    {
        "symptom": "hair loss",
        "disease": "Alopecia",
        "severity": "Mild to Moderate",
        "description": "Noticeable thinning or patches of hair loss, commonly on the scalp.",
        "medication": "Minoxidil topical, Biotin supplements",
        "precautions": "Gentle hair care, avoid harsh chemicals",
        "treatment": "Topical treatments, address deficiencies",
        "diet": "Protein-rich foods, iron, biotin",
        "when_to_see_doctor": "If rapid or patchy loss"
    }
]

# Create DataFrame and save as CSV
df_enhanced = pd.DataFrame(enhanced_medical_data)
df_enhanced.to_csv('enhanced_medical_dataset.csv', index=False)

print("Enhanced medical dataset created with the following columns:")
print(df_enhanced.columns.tolist())
print(f"\nDataset shape: {df_enhanced.shape}")
print("\nFirst few rows:")
print(df_enhanced[['symptom', 'disease', 'medication']].head())