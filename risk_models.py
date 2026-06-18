
# just importing the functions and data from another files
from medical_knowledge import NORMAL_RANGES, DISEASE_WEIGHTS
from abnormality_detector import compute_deviation

''' In this part of the project, we define how to calculate the risk of a patient having a certain disease based on their medical measurements.
 The 'compute_disease_risk' function takes in the patient's medical data and the name of the disease we want to assess.
 It uses the normal ranges and weights defined in the 'medical_knowledge' module/file to calculate a risk score.

 in below function,
 patient_data: a dictionary containing the patient's medical measurements,
 disease_name: the name of the disease we want to assess risk,
   for (e.g., "diabetes", "heart_disease", "liver_disease") 
'''
def compute_disease_risk(patient_data, disease_name): #
    weights = DISEASE_WEIGHTS[disease_name]  # dictionary from 'medical_knowledge.py' .

    # Give each disease a unique baseline risk
    base_risks = {
        "Diabetes": -2.3,      # ~9.1%
        "Heart Disease": -2.8, # ~5.7%
        "Liver Disease": -3.2  # ~3.9%
    }
    risk_score = base_risks.get(disease_name, -2.5)

    for parameter in weights:   # Loop through each medical parameter that is relevant for the disease (as defined in the weights dictionary).

        if parameter not in patient_data:
            continue

        value = patient_data[parameter]  # Get the actual measurement value for the parameter from the patient's data.
        low, high = NORMAL_RANGES[parameter]  # dictionary from 'medical_knowledge.py' .

        deviation = compute_deviation(value, low, high, parameter=parameter)  # function from 'abnormality_detector.py' .

        weight = weights[parameter]
        
        # Scale the contribution so significant deviations overcome the negative base risk
        risk_score = risk_score + deviation * weight * 6.0 

    return risk_score

