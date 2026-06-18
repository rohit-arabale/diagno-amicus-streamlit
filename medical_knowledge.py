

#This part of your project defines basic medical knowledge that the system uses to judge,whether a patient is healthy or at risk of certain diseases.
 

'''This dictionary defines the normal ranges for various medical parameters.
 The keys are the parameter names, and the values are tuples containing the 'minimum' and 'maximum' healthy values for that parameter.'''
NORMAL_RANGES = {  

    # Diabetes
    "Glucose": (70, 100),  # parameter : (minimum healthy value, maximum healthy value)
    "BMI": (18.5, 24.9),
    "Insulin": (2, 25),

    # Heart
    "Cholesterol": (125, 200),   # parameter : (minimum healthy value, maximum healthy value)
    "Resting BP": (80, 120),
    "Max Heart Rate": (60, 190),

    # Liver 
    "Bilirubin": (0.1, 1.2),    # parameter : (minimum healthy value, maximum healthy value)
    "ALT": (7, 56),
    "AST": (10, 40)
}


# Clinical importance weights
'''This dictionary tells the system:
 How important each medical parameter is for detecting a disease
 Each disease has weights assigned to related measurements.
 Weights are numbers between 0 and 1.
 Higher weight = more important indicator.

 For example, for diabetes:
 - Glucose has a weight of 0.5 (most important)
 - BMI has a weight of 0.3 (important but less than glucose)
 - Insulin has a weight of 0.2 (least important among the three)
 This helps the system prioritize which measurements to focus on when assessing risk for each disease.
 '''
DISEASE_WEIGHTS = {

    "Diabetes": {
        "Glucose": 0.5, #most important indicator for diabetes
        "BMI": 0.3,
        "Insulin": 0.2
    },

    "Heart Disease": {
        "Cholesterol": 0.4, #most important indicator for heart disease
        "Resting BP": 0.3,
        "Max Heart Rate": 0.3
    },

    "Liver Disease": {
        "Bilirubin": 0.4, #most important indicator for liver disease
        "ALT": 0.3,
        "AST": 0.3
    }
}