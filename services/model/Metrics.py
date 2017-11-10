""" Metrics Settings for Waves Project

"""

class Metrics(object):
    
    def __init__(self, frequency="PT15S", reporters="console"):
        self.frequency = frequency
        self.reporters = reporters
    
    def to_dict(self):
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['frequency'] = self.frequency
        info['reporters'] = self.reporters
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        metrics = Metrics()
        
        metrics.frequency = info['frequency'] 
        metrics.reporters = info['reporters'] 
        
        return metrics