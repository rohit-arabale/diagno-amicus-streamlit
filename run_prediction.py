
# just importing the fucntions and data from another files
from clinical_reasoner import ClinicalReasoner
from engine import explain_prediction


reasoner = ClinicalReasoner() # function from 'clinical_reasoner.py'

patient = {} # dictionary to store the patient's medical data, which will be filled with user input for various health parameters ..

print("\n|| Enter the Patient Values:")

patient["Glucose"] = float(input("- Glucose: "))
patient["BMI"] = float(input("- BMI: "))
patient["Insulin"] = float(input("- Insulin: "))

patient["Cholesterol"] = float(input("- Cholesterol: "))
patient["Resting BP"] = float(input("- Resting BP: "))
patient["Max Heart Rate"] = float(input("- Max Heart Rate: "))

patient["Bilirubin"] = float(input("- Bilirubin: "))
patient["ALT"] = float(input("- ALT: "))
patient["AST"] = float(input("- AST: "))

ranked = reasoner.diagnose(patient)  # The 'diagnose' method of the 'reasoner' (ClinicalReasoner instance) is called with the patient's data to get a ranked list of disease probabilities based on the input measurements.

print("\n|| Disease Probabilities :")
for disease, prob in ranked:  # Loop through the ranked list of diseases and their associated probabilities..
    print("-+- "+ disease, "=", round(prob, 3)) # Each disease and its probability is printed, with the probability rounded to three decimal places for better readability.

best = ranked[0][0]  # The top-ranked disease (the one with the highest probability) is extracted from the ranked list. 'ranked[0]' gives the first tuple (disease, probability)..

# below ,The 'explain_prediction' function from 'engine.py' file , is called with the patient's data and the best predicted disease to provide a clinical explanation for why that disease was predicted,
# based on the patient's measurements and how they deviate from normal ranges.
explain_prediction(patient, best) 