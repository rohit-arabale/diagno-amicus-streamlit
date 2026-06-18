
# just importing the functions and data from another files
from medical_knowledge import NORMAL_RANGES, DISEASE_WEIGHTS
from abnormality_detector import compute_deviation

'''
 The below function ' explain_prediction(patient_data, disease_name) ' provides a simple clinical explanation for why the system predicted a particular disease.
 It checks the medical parameters related to that disease (using importance weights from the medical knowledge base),
 compares the patient's values with normal healthy ranges, and calculates how abnormal each value is using the deviation function.
 If a parameter is significantly abnormal (above a chosen threshold, here 0.2), the function prints that the parameter contributes to the disease risk. In short,
 it makes the AI's decision transparent by showing which abnormal health measurements influenced the prediction.
'''
def explain_prediction(patient_data, disease_name):

    print("-------------------+ + Diagonose Prediction Result + +----------------")

    print("\n||||||---> Predicted Disease : ", disease_name)

    weights = DISEASE_WEIGHTS[disease_name]  # dictionary from 'medical_knowledge.py' .

    for p1 in weights:

        if p1 not in patient_data:
            continue

        value = patient_data[p1] #dictionary from 'clinical_reasoner.py' .
        low, high = NORMAL_RANGES[p1] # dictionary from 'medical_knowledge.py' .

        deviation = compute_deviation(value, low, high) # function from 'abnormality_detector.py' .

        if deviation > 0.2:
            print(f"- - '{p1}' is Abnormal ---> Contributes to the Risk of : {disease_name}") 