""" Project Global Information """

class ProjectInfo(object):
    
    def __init__(self, name="", description="", license="", version=""):
        self.name        = name
        self.description = description
        self.license     = license
        self.version     = version
        self.createdAt   = ""
        
    def to_dict(self):
        
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['name']        = self.name
        info['description'] = self.description
        info['license']     = self.license
        info['version']     = self.version
        info['createdAt']   = self.createdAt
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        projectInfo = ProjectInfo()
        
        projectInfo.name        = info['name'] 
        projectInfo.description = info['description'] 
        projectInfo.license     = info['license'] 
        projectInfo.version     = info['version'] 
        projectInfo.createdAt   = info['createdAt'] 
        
        return projectInfo