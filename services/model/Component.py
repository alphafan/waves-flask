""" Component in Workflow

Component in workflow has severals information that we need to keep:
- cmptType    : Component Type, i.e. RawSource etc.
- settings    : Dictionary of key-value settings that will be written into TriG configuration
- ui_left     : Location of component to left of panle, i.e. 68px
- ui_top      : Location of component to the top of panel, i.e. 80px
- id          : Component's HTML ID

"""

class Component(object):
    
    def __init__(self, id=None, cmptType='', settings={}, ui_left=0 , ui_top=0):
        self.cmptType   = cmptType
        self.settings   = settings
        self.ui_left    = ui_left
        self.ui_top     = ui_top
        self.id         = id
    
    def to_dict(self):
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['cmptType']    = self.cmptType
        info['settings']    = self.settings
        info['ui_left']     = self.ui_left
        info['ui_top']      = self.ui_top
        info['id']          = self.id
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        cmpt = Component()
        
        cmpt.cmptType   = info['cmptType'] 
        cmpt.settings   = info['settings'] 
        cmpt.ui_left    = info['ui_left'] 
        cmpt.ui_top     = info['ui_top'] 
        cmpt.id         = info['id'] 
        
        return cmpt
    
    def add_setting(self, key, value):
        """ Add settings for current component
        
        Args:
            key     : string
            value   : string
        """
        self.settings[key] = value