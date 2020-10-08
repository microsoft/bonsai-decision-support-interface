#!/usr/bin/env python3
import docker, requests # Docker sdk for python
import numpy as np
import pandas as pd
import datetime, time

class ExportedBrainPredictor():
    ''' creates a concept from an exported Brain Docker Container, from which we can get control actions
    '''

    def __init__(self, predictor_url: str, control_period: int=1):
        self.control_period = control_period
        self.predictor_url = predictor_url
    
    def is_control_iteration(self, iteration: int):
        ''' returns True if iteration is a control iteration for this concept
        '''
        #print('iteration: {}'.format(iteration))
        if iteration % self.control_period == 0:
            is_control_iteration = True
        else:
            is_control_iteration = False
        return is_control_iteration

    def get_action(self, state: dict, iteration: int = 0) -> dict:
        """ Get action from predictor, given a state
        
        Returns
        -------
        action
        """
        exported_brain_url = '{}/v1/prediction'.format(self.predictor_url)
        #print(exported_brain_url)
        if self.is_control_iteration(iteration) == True:
            response = requests.get(exported_brain_url, json = state)
            action = response.json()
        else:
            action = self.last_action
        self.last_action = action
        return action

def list_available_brain_images():
    """ Returns list of running containers corresponding to exported brains available to run 
    
    Returns
    -------
    list_brain_containers
    """
    client = docker.from_env()
    images = client.images
    print(images.list())    

def launch_predictor_server(brain_image_name: str, port: int = 5000) -> str:
    ''' creates a predictor from an exported brain container, return its rootrul
    '''
    client = docker.from_env()
    concept_predictor = client.containers.run(
        brain_image_name,
        detach = True, 
        ports = {'5000':port}
        )
    predictor_url = 'http://localhost:{}'.format(port)
    print(
        'creating concept_predictor from brain image {} \n\
            concept_predictor serving at http://localhost:{}'.format(brain_image_name,port)
    )
    return predictor_url

if __name__ == "__main__":
    print("test two exported brains predictors")
    
    list_available_brain_images()
    
    C1_url = 'http://localhost:5000'
    C1 = ExportedBrainPredictor(predictor_url = C1_url, control_period = 1)

    RadiusOfPlate = 0.1125
    MaxVelocity = 1.0

    for iteration in range(3):
        state = {
            'ball_x': np.random.rand() * RadiusOfPlate,
            'ball_y': np.random.rand() * RadiusOfPlate,
            'ball_vel_x': np.random.rand() * MaxVelocity,
            'ball_vel_y': np.random.rand() * MaxVelocity,
            'target_x': np.random.rand() * RadiusOfPlate,
            'target_y': np.random.rand() * RadiusOfPlate,
        }
        action1 = C1.get_action(state)
        print('action from concept1: {}'.format(action1))