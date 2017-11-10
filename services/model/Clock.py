""" Clock Settings for Waves Configuration

This configuration is used for the simulated waves acceleration settings

"""

class Clock(object):
    
    def __init__(self, 
                 startDate="2013-12-31T23:00:00Z",
                 endDate="2015-10-05T11:24:00Z",
                 duration="PT24H",
                 localTimeZone="False",
                 acceleration="80"):
        self.startDate      = startDate
        self.endDate        =  endDate
        self.duration       = duration
        self.localTimeZone  = localTimeZone
        self.acceleration   = acceleration
    
    def to_dict(self):
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['startDate']       = self.startDate
        info['endDate']         = self.startDate
        info['duration']        = self.startDate
        info['localTimeZone']   = self.localTimeZone
        info['acceleration']    = self.acceleration
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        clock = Clock()
        
        clock.startDate     = info['startDate'] 
        clock.endDate       = info['endDate'] 
        clock.duration      = info['duration'] 
        clock.localTimeZone = info['localTimeZone'] 
        clock.acceleration  = info['acceleration'] 
        
        return clock