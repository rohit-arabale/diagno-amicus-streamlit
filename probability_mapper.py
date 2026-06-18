

import math

'''
This function takes a risk score (which can be any real number) and maps it to a probability between 0 and 1 using the probablity  function.

    so = 1 / (1 + math.exp(-x))
      This mapping allows us to interpret the risk score as a probability of having the disease, where:
      - A risk score of 0 corresponds to a probability of 0.5 (indicating an average risk).
      - Positive risk scores correspond to probabilities greater than 0.5 (indicating higher risk).
      - Negative risk scores correspond to probabilities less than 0.5 (indicating lower risk).
This is useful for making the output of the risk assessment more interpretable and actionable for healthcare providers and patients.'''

def probability(x):   # defining a function
    so = 1 / (1 + math.exp(-x))
    return so

''' ==> 'math.exp(-x)' , calculates the exponential of -x, which is a key part of the sigmoid function. 
    The probablity function transforms any real-valued number into a value between 0 and 1, 
    making it ideal for mapping risk scores to probabilities. 
    The output of this function can be interpreted as the probability of having a disease based on the calculated risk score.
'''