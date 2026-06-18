
'''
 The function ' evaluate(reasoner, dataset) ' is used to measure how accurate the disease prediction system is.
 It tests the model on a dataset of patient records where the correct disease is already known.
 For each record, the function takes the patient's data, uses the reasoning system (reasoner.diagnose) to predict the disease,
 and compares the prediction with the actual (true) disease label. If they match, it counts as a correct prediction. 
 After checking all records, it calculates accuracy by dividing the number of correct predictions by the total number of cases.
 In simple terms, this function evaluates how well the AI doctor performs by calculating its prediction accuracy..
'''

def evaluate(reasoner, dataset):

    correct = 0

    for record in dataset:  # Loop through each patient record in the dataset, where each record contains the patient's medical data and the true disease label.

        patient_data = record["data"] # Extract the patient's medical data from the record, which is expected to be a dictionary of measurements.
        true_disease = record["label"] # Extract the true disease label from the record, which is the correct diagnosis for that patient.

        ranked = reasoner.diagnose(patient_data) # Using the 'diagnose' method of the 'reasoner' (which is an instance of the 'ClinicalReasoner' class) to get a ranked list of disease predictions based on the patient's data.

        prediction = ranked[0][0] # The top-ranked prediction (the disease with the highest calculated probability) is extracted from the ranked list. 'ranked[0]' gives the first tuple (disease, probability), and '[0]' extracts just the disease name from that tuple.

        if prediction == true_disease: # If the predicted disease matches the true disease label, it counts as a correct prediction, and we increment the 'correct' counter by 1.
            correct = correct + 1

    accuracy = correct / len(dataset) # After processing all records, we calculate the accuracy by dividing the number of correct predictions by the total number of records in the dataset (len(dataset)).

    return accuracy