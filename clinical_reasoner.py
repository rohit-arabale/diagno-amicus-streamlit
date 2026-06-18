

# just importing the functions and data from another files

from medical_knowledge import NORMAL_RANGES, DISEASE_WEIGHTS
from risk_models import compute_disease_risk
from probability_mapper import probability

'''
class in python : is a blueprint for creating objects. It defines a set of attributes and methods that the created objects will have.

 This class 'ClinicalReasoner' is responsible for taking a patient's medical data and using the risk models and probability mapping,
 to provide a diagnosis or risk assessment for multiple diseases.

 The 'ClinicalReasoner' class has a method called 'diagnose' which takes in the patient's medical data,
 computes the risk for each disease using the 'compute_disease_risk' function, maps that risk to a probability using the
 'sigmoid' function, and then ranks the diseases based on their probabilities to provide a final diagnosis or risk assessment.
'''

class ClinicalReasoner: 
    def __init__(self): # The '__init__' method is a special method, in Python classes that is called when an object is instantiated. It is used to initialize the attributes of the class.
        self.diseases = ["Diabetes", "Heart Disease", "Liver Disease"] # This line initializes an attribute 'diseases' which is a list of the diseases that the clinical reasoner will assess risk for.

    def diagnose(self, patient_data): # The 'diagnose' func/method takes in 'patient_data', which is expected to be a dictionary containing the patient's medical measurements.

        results = {} # initializes an empty dictionary called 'results' which will be used to store the calculated probabilities for each disease.

        for disease in self.diseases:

            risk = compute_disease_risk(patient_data, disease) #function from 'risk_modeals.py'.
            prob = probability(risk)   #function from 'prbability_mapper.py' .

            results[disease] = prob # This line adds an entry to the 'results' dictionary, where the key is the disease name and the value is the calculated probability of having that disease based on the patient's data.

        ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
        '''
        in above line 'ranked', sorts the diseases based on their calculated probabilities in descending order.

          ==>>> 'results.items()' returns a list of tuples (disease, probability).  
          ==>>> 'key=lambda x: x[1]' tells the sorting function to sort based on the second element of the tuple, which is the probability.
          ==>>> 'reverse=True' sorts the list in descending order, so diseases with higher probabilities will come first in the list.
        The sorted list of tuples is stored in the variable 'ranked', which can then be used to provide a ranked diagnosis or risk assessment for the patient.
        '''

        return ranked # it returns the list 
    
