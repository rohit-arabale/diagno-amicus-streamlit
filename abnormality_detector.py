
'''
 This function, calculates how much a given medical parameter value deviates from its normal range.
 It takes the actual value and the normal low and high values as input, and returns a deviation score.
 The score is calculated based on how far the value is from the midpoint of the normal range, normalized by the width of the range.
 A higher score indicates a greater deviation from normal, which may suggest a higher risk for that particulardisease.
'''

def compute_deviation(value, normal_low, normal_high, parameter=None):
    if parameter == "Max Heart Rate":
        if value < normal_low:
            # Calculate how far below the limit relative to the limit itself
            return ((normal_low - value) / normal_low) * 5.0
        elif value <= normal_high:
            return 0
        else:
            return -0.2
    else:
        if value > normal_high:
            # Calculate how far above the limit relative to the limit itself
            return ((value - normal_high) / normal_high) * 5.0
        elif value >= normal_low:
            return 0
        else:
            return -0.2

