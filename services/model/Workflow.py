""" Workflow Model

Workflow model contains information of the workflow created by Waves User.
It consists of two parts of informations:
    - List of components in the workflow
    - List of links between components in the workflow

"""

from services.model.Component import Component
from services.model.Link import Link
import os

class Workflow(object):
    
    def __init__(self, cmpt_list = [], link_list = []):
        self.cmpt_list = cmpt_list
        self.link_list = link_list
    
    def to_dict(self):
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        cmpt_dict_list = []
        link_dict_list = []
        
        for cmpt in self.cmpt_list:
            cmpt_dict_list.append(cmpt.to_dict())
        for link in self.link_list:
            link_dict_list.append(link.to_dict())
        
        info['cmpt_list'] = cmpt_dict_list
        info['link_list'] = link_dict_list
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        workflow = Workflow()
        
        workflow.cmpt_list = []
        workflow.link_list = []
        
        cmpt = Component()
        link = Link()
        
        cmpt_dict_list = info['cmpt_list']
        link_dict_list = info['link_list']
        
        # Iterate each component and list to append to workflow
        for cmpt_dict in cmpt_dict_list:
            workflow.cmpt_list.append( cmpt.parse_from_dict( cmpt_dict ) )
        for link_dict in link_dict_list:
            workflow.link_list.append( link.parse_from_dict( link_dict ) )
        
        return workflow
    
    """
        Component related processing
    """
    
    def add_cmpt(self, cmpt):
        """ Append a new component to workflow
        
        Args:
            cmpt: Component: a new component that will be added to the current workflow
        """
        self.cmpt_list.append( cmpt )
        print( "Add Component", cmpt.id )
    
    def del_cmpt(self, cmpt):
        """ Delete the component from workflow
        
        Args:
            cmpt: Component: the component that will be deleted from the workflow
        """
        self.cmpt_list.remove(cmpt)
        print( "Delete Component", cmpt.id )
    
    def del_cmpt_by_id(self, cmptId):
        """ Delete the component by id

        :param cmptId: id of the component to be removed
        :return:
        """
        cmpt = self.get_cmpt_by_id(cmptId)
        if cmpt != None:
            self.del_cmpt(cmpt)
        
    def get_cmpt_by_id(self, cmptId):
        """ Get component from its id

        :param cmptId: id of the component to get
        :return: component
        """
        for cmpt in self.cmpt_list:
            if cmpt.id == cmptId:
                return cmpt
        return None
    
    def update_component_location(self, cmptId, ui_left, ui_top):
        """ Update component location in the UI

        :param cmptId: id of current component
        :param ui_left: Component location to the left of the workflow space
        :param ui_top:  Component location to the top of workflow space
        :return:
        """
        for index, cmpt in enumerate(self.cmpt_list):
            if cmpt.id == cmptId:
                self.cmpt_list[index].ui_left = ui_left
                self.cmpt_list[index].ui_top = ui_top
                print( "Update Component Location : ", cmpt.id, cmpt.ui_left ,cmpt.ui_top )
    
    def save_component_settings(self, cmptId, settings):
        """ Save component settings

        :param cmptId: Id of the component to be saved settings
        :param settings: Key-value dictionary of the settings to be setted for component
        :return:
        """
        for index, cmpt in enumerate(self.cmpt_list):
            if cmpt.id == cmptId:
                self.cmpt_list[index].settings = settings
                print( "Save Component Settings : ", cmpt.id, cmpt.settings )
    
    """
        Links related processing
    """
    
    def add_link(self, link):
        """ Append a new link to the current workflow

        :param link: Link to be added
        :return:
        """
        self.link_list.append( link )
        print( "Add link", link.srcCmpt.id, link.trgCmpt.id )
    
    def add_link_with_cmpts(self, srcCmpt, trgCmpt):
        """ Add a new new by specifyting the source component and target component

        :param srcCmpt: source component
        :param trgCmpt: target component
        :return:
        """
        link = Link(srcCmpt=srcCmpt, trgCmpt=trgCmpt)
        self.add_link(link)

    def add_link_with_cmpt_ids(self, srcCmptId, trgCmptId):
        """ Add a new link to workflow by giving the id of source and target component

        :param srcCmptId: id of source component
        :param trgCmptId: id of target component
        :return:
        """
        srcCmpt = self.get_cmpt_by_id(srcCmptId)
        trgCmpt = self.get_cmpt_by_id(trgCmptId)
        if srcCmpt != None and trgCmpt != None:
            self.add_link_with_cmpts(srcCmpt, trgCmpt)
    
    def get_link_by_cmpt_ids(self, srcCmptId, trgCmptId):
        """ Get the link by giving source component and target component ids

        :param srcCmptId: id of source component
        :param trgCmptId: id of target component
        :return: The link which connects two components
        """
        for link in self.link_list:
            if link.srcCmpt == self.get_cmpt_by_id(srcCmptId) and link.trgCmpt == self.get_cmpt_by_id(trgCmptId):
                return link
    
    def del_link(self, link):
        """ Delete link from workflow

        :param link: link to be deleted from workflow
        :return:
        """
        self.link_list.remove(link)
        print( "Delete Link", link.srcCmpt.id, link.trgCmpt.id )
        
    def del_link_by_src_cmpt(self, srcCmpt):
        """ Delete all the links that takes the srCompt as the source component

        :param srcCmpt: Source component where the links are dragged out
        :return:
        """
        for link in self.link_list:
            if link.srcCmpt == srcCmpt:
                self.del_link(link)
        
    def del_link_by_src_cmpt_id(self, srcCmptId):
        """ Delete all the links that comes from the source component with srcCmptId as its id

        :param srcCmptId: Id of the source component
        :return:
        """
        srcCmpt = self.get_cmpt_by_id(srcCmptId)
        self.del_link_by_src_cmpt(srcCmpt)
        
    def del_all_links(self, cmptId):
        """ Delete all the links that either comes from the component or links to the component

        :param cmptId: Id of the the component
        :return:
        """
        cmpt = self.get_cmpt_by_id(cmptId)
        
        for link in self.link_list:
            if link.srcCmpt == cmpt or link.trgCmpt == cmpt:
                self.del_link(link)
        
    def save_link_settings(self, link, settings):
        """ Save the link's settings

        Specific here, it's for the setting of window span since the window span is a settings of link

        :param link: The link that will save settings
        :param settings: Settings of the link
        :return:
        """
        for index, i_link in enumerate(self.link_list):
            if i_link == link:
                print( "Save Link Settings : ", link.srcCmpt.id, link.trgCmpt.id, settings )
                self.link_list[index].settings = settings
                
    def save_link_settings_by_cmpt_ids(self, srcCmptId, trgCmptId, settings):
        """ Save link settings by the link source id and target id

        :param srcCmptId: source component id of the link
        :param trgCmptId: target component id of the link
        :param settings: settings that will given to the link
        :return:
        """
        link = self.get_link_by_cmpt_ids(srcCmptId, trgCmptId)
        self.save_link_settings(link, settings)
        
    def get_default_workflow(self):
        """ Get a default workflow for Waves

        The default workflow is saved in the default_workflow.json file.

        :return: a default workflow in json string
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open( dir_path + '/default_workflow.json', 'r') as file:
            data=file.read()
        return data