from mesa import Agent
import logging
import numpy as np
import math as m
from flock.logging import *
#import pytest
from flock.vectors import *

class Fish(Agent):
    """ An agent with body length, position, scalar speed, direction."""
    
    def __init__(self, unique_id, model, init_x, init_y):
        super().__init__(unique_id, model)
        self.heading = unit(np.array([init_x, init_y])) # heading vector of agent

    def head(self):
        self.newPos = np.asarray(self.pos) + self.model.parameters.cruiseSpeed * self.newHeading

    def group(self, radius, include_center = False):
         # pos: FloatCoordinate, radius: float, include_center: bool = True
        self.model.space.get_neighbors(self.pos, radius, include_center)

    def align(self):
        """ ALIGNMENT """

        alignmentGroup = self.group(self.model.parameters.alignmentRadius)

        if alignmentGroup:
            # if there are other agents within the alignement area:

            alignmentVector = np.array([0, 0])

            for neighbor in alignmentGroup:
                alignmentVector += neighbor.heading

            alignmentDirection = direction( alignmentVector, len(alignmentGroup) )

            return self.model.parameters.alignmentWeight * unit(alignmentDirection - self.heading)

        else:
            return self.heading

    def cohese(self):
        """ COHESION
        attraction to the center of gravity of the group within the cohesion area """

        cohesionGroup = self.group(self.model.parameters.cohesionRadius)

        if cohesionGroup:
            # if there are other agents within the cohesion area:

            cohesionVector = np.array([0, 0])

            for neighbor in cohesionGroup:
                distance = np.asarray(neighbor.pos) - np.asarray(self.pos)
                cohesionVector += unit(distance)

            return force(self.model.parameters.cohesionWeight, cohesionVector, len(cohesionGroup))
        else:
            return np.array([0, 0])

        
    def step(self):
        """ The agent takes into account three areas:
        - cohesion (radius defaulted to 2)
        - alignment (radius defaulted to 5)
        - separation (radius defaulted to 15) """

        # HEADING
        self.newHeading = self.align() + self.cohese()
        self.head()
               
    def advance(self):
        """Apply changes incurred in step(), i.e. update agent's position and heading"""  
        logging.info("Agent {0} moves from {1}".format(self.unique_id, self.pos))      
        self.model.space.move_agent(self, self.newPos)
        self.heading = self.newHeading
        logging.info(" to {0}\n".format(self.pos))