from math import cos, sin, sqrt, pi

class Earthquake:
    def __init__(self, magnitude, fault_heading, fault_dip, fault_slip):
        # apply Wells-Coppersmith Model
        rupture_area = 10 ** (0.91 * magnitude - 3.49)
        average_displacement = 10 ** (0.69 * magnitude - 4.80)
        # caculate geometry values
        self.radius = sqrt(rupture_area / pi)
        self.uplift = average_displacement * sin(pi / 180 * fault_slip) * sin(pi / 180 * fault_dip)
        self.heading = fault_heading
    
    def get_uplift(self, x, y):
        if (x ** 2 + y ** 2 > self.radius ** 2):
            return 0
        first_plate = (cos(pi / 180 * self.heading) * x) - (sin(pi / 180 * self.heading) * y) >= 0
        return self.uplift if first_plate else -1 * self.uplift
