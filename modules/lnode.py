import random
import simpy  # Import the SimPy module
import yaml  # For configuration file parsing
import os  # For file path operations
import math

# Load the main configuration from the YAML file
with open('config.yaml', 'r') as file:
    main_config = yaml.safe_load(file)

# Function to load node configuration
def load_node_config(node_name):
    node_config_path = main_config['nodeConfig'].get(node_name)
    if node_config_path and os.path.exists(node_config_path):
        with open(node_config_path, 'r') as file:
            return yaml.safe_load(file)
    return None

# Example usage
"""node_name_to_check = "node1"
node_config = load_node_config(node_name_to_check)

if node_config:
    dev_eui = node_config['node']['DevEUI']
    print(f"Node {node_name_to_check} with DevEUI {dev_eui} exists.")
else:
    print(f"Node {node_name_to_check} does not exist.")
"""
# Define the node class
class LoraNode:
    def __init__(self, env: simpy.Environment, nodeName):
        self.env = env
        self.nodeName = nodeName

        # Now the function will check if there is a config for the given node in config.yaml
        # If there is a config for the node, it will load the values from the config file
        # Otherwise, it will use default values

        node_config = load_node_config(nodeName)['node']
        if node_config:
            self.devEUI = node_config.get('DevEUI', random.randint(0, 2**64))
            self.spreadingFactor = node_config.get('SpreadingFactor', 7)
            self.minFrequency = node_config.get('FrequencyRange')[0]
            self.maxFrequency = node_config.get('FrequencyRange')[1]
            self.transmissionPower = node_config.get('TransmissionPower', 14)
            self.dutyCycleLimits = node_config.get('DutyCycleLimits', 1)
            self.sensorData = node_config.get('Sensor', {
                'type': 'temperature',
                'minValue': 0,
                'maxValue': 100,
                'unit': 'C',
                'frequency': 60,
                'function': "sin",
                'noise': 0.1
                'bias': 0.5 # Error bias
            })
        
    def generate_signal(self):
        # Generate the signal based of the function from sensorData
        # types include, sin, random, etc.
        # The output will squished to adjust the minValue and maxValue
        minVal = self.sensorData['minValue']
        maxVal = self.sensorData['maxValue']
        if self.sensorData['function'] == 'sin':
            value = (maxVal - minVal) * (1 + random.random() * math.sin(2 * math.pi * self.env.now / self.sensorData['frequency'])) / 2 + minVal
        elif self.sensorData['function'] == 'random':
            value = (maxVal - minVal) * random.random() + minVal
        
        # Placeholder for other functions

        # Add bias to the value
        value += self.sensorData['bias']

        return value
    
    def add_noise(self, signal):
        # Add noise to the signal
        return signal + random.gauss(0, self.sensorData['noise'])

    def assemble_packet(self):
        # Assemble the packet with the signal
        signal = self.generate_signal()
        signal = self.add_noise(signal)
        return {
            'DevEUI': self.devEUI,
            'SpreadingFactor': self.spreadingFactor,
            'Frequency': random.uniform(self.minFrequency, self.maxFrequency),
            'TransmissionPower': self.transmissionPower,
            'Noise': self.sensorData['noise'],
            'Bias': self.sensorData['bias'],
            'Time': self.env.now,
            'Signal': signal
        }

    def transmit_packet(self, packet):
        # Placeholder for packet transmission
        pass