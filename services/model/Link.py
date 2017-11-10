""" Link of Workflow

Link is to describe the connection between 2 components in workflow
Three informations are needed in a Link:
- srcCmpt : Source Component
- trgCmpt : Target Component
- settings : Settings related with link, in our case, it's only for window span between RDF Stream and Filter 

"""

from services.model.Component import Component

class Link(object):
    
    def __init__(self, srcCmpt=None, trgCmpt=None, settings={}):
        self.srcCmpt    = srcCmpt
        self.trgCmpt    = trgCmpt
        self.settings   = settings

    def to_dict(self):
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['srcCmpt']     = self.srcCmpt.to_dict()
        info['trgCmpt']     = self.trgCmpt.to_dict()
        info['settings']    = self.settings
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        link = Link()        
        
        srcCmpt = Component()
        srcCmpt.cmptType    = info['srcCmpt']['cmptType'] 
        srcCmpt.settings    = info['srcCmpt']['settings'] 
        srcCmpt.ui_left     = info['srcCmpt']['ui_left'] 
        srcCmpt.ui_top      = info['srcCmpt']['ui_top'] 
        srcCmpt.id          = info['srcCmpt']['id'] 
        
        trgCmpt = Component()
        trgCmpt.cmptType    = info['trgCmpt']['cmptType'] 
        trgCmpt.settings    = info['trgCmpt']['settings'] 
        trgCmpt.ui_left     = info['trgCmpt']['ui_left'] 
        trgCmpt.ui_top      = info['trgCmpt']['ui_top'] 
        trgCmpt.id          = info['trgCmpt']['id'] 
        
        link.srcCmpt    = srcCmpt
        link.trgCmpt    = trgCmpt
        link.settings   = info['settings'] 
        
        return link