""" Cluster Information Settings for Waves Configuration

This configuration is used for specify the IP and Port for each services

"""

class ClusterInfo():
    
    def __init__(self, 
                 zookeeperHosts = ["localhost:2181"],
                 kafkaHosts = ["localhost:9092"],
                 redisHost = "localhost:6379",
                 mongoHost = "localhost:27017",
                 influxHost = "localhost:8086"):
        self.zookeeperHosts = zookeeperHosts
        self.kafkaHosts     = kafkaHosts
        self.redisHost      = redisHost
        self.mongoHost      = mongoHost
        self.influxHost     = influxHost

    def to_dict(self):
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['zookeeperHosts']  = self.zookeeperHosts
        info['kafkaHosts']      = self.kafkaHosts
        info['redisHost']       = self.redisHost
        info['mongoHost']       = self.mongoHost
        info['influxHost']      = self.influxHost
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        clusterInfo = ClusterInfo()
        
        clusterInfo.zookeeperHosts  = info['zookeeperHosts'] 
        clusterInfo.kafkaHosts      = info['kafkaHosts'] 
        clusterInfo.redisHost       = info['redisHost']
        clusterInfo.mongoHost       = info['mongoHost']
        clusterInfo.influxHost      = info['influxHost'] 
        
        return clusterInfo