# -*- coding: utf-8 -*-

""" FileHandler deals with files of the project space folder and the project folder inside project space folder

This class is used for:
    - Set Up Project Space / Project Folder at Local Directory
    - Get list of existing projects
    - Save uploaded files from stream sources, static feed
    - Save the workflow UI in html tags in text file
    - Load project from files -> Project model format, TriG format and Json format
    - Delete project
"""

from werkzeug.utils import secure_filename

from os.path import expanduser
import os
import shutil
import json

from services.model import Project

class FileHandler(object):
    
    """
        Init function
    """
    
    def __init__(self):
        """ Initial function for some default directory locations
        
        Params:
            self.directory: 
                Project space directory
                This is the path where we save the project files and configurations
                The value of this directory: /{user.home}/Documents/waves_project_spaces
            self.tmpDir:
                Temporal directory is used for two things:
                1. Save the temp dockerfile
                2. During the time we create a project, user may specify and upload some data files,
                    for example, the stream source files, static feeds etc. The tmpDir is where
                    we save there temp files. Once user click on create project button, all the temp
                    data will be moved to the project folder
            self.tmpDataDir:
                Temporal data folder
                Save the temp data files which are uploaded by users
            self.tmpRawSourceDir:
                Sub data folder for Raw Source
            self.tmpRdfSourceDir:
                Sub data folder for RDF Source
            self.tmpStaticFeedDir:
                Sub data folder for Static Doc Feed
        """
        self.directory = expanduser("~") + "/Documents/waves_project_spaces"
        self.tmpDir = self.directory + '/tmp'
        self.tmpDataDir = self.tmpDir + "/instance/Data"
        self.tmpRawSourceDir = self.tmpDataDir + "/RawSource"
        self.tmpRdfSourceDir = self.tmpDataDir + "/RdfSource"
        self.tmpStaticFeedDir = self.tmpDataDir + "/StaticFeed"
    
    """
        Set Up Project Space / Project Folders
    """
    
    def setup_project_space_folder(self):
        """ Set up project space folder
        
        The project space folder will be located at /{user.home}/Documents/waves_project_space
        
        The set up process will do:
            - Create project space folder if it doesn't exist
            - Copy docker folder to the tmp folder
            - Empty all the tmp data folder
        
        """
        
        if not self._exists_dir( self.directory ):
            # If this folder doesn't exist (the first time launch the program), we will create one. 
            self._create_dir( self.directory )
        else:
            # If already exists, do nothing
            pass
        
        self._empty_dir( self.tmpDir )
        
        # Copy docker to tmp folder
        docker_folder = os.path.join(os.path.dirname(__file__), 'docker-standalone')
        self._copy_dir(docker_folder, self.tmpDir)
        
        # Empty the source data folder
        self._empty_dir( self.tmpDataDir )
        self._empty_dir( self.tmpRawSourceDir )
        self._empty_dir( self.tmpRdfSourceDir )
        self._empty_dir( self.tmpStaticFeedDir )
        
        
    def setup_project_folder(self, project):
        """ Set up project folder

        When user create a new project, we need to save the project somewhere in his machine.
        We choose the project folder location as: /{user.home}/Documents/waves_project_space/NEW_PROJECT_NAME

        Copy the tmp folder --> project folder
        Write the project information as trig and json file

        After setop, the structure of directory is:
        | -- PROJECT_NAME.trig
        | -- PROJECT_NAME.json
        | -- workflow.txt
        | -- docker-standalone
            | -- docker-compose.yml
            | -- instance
                | -- Configuration
                | -- Data
                | -- ....

        :param project: Project model
        :return:
        """
        
        project_name = project.projectInfo.name
        
        # Create an empty project directory
        project_dir = self.directory + "/" + project_name
        self._empty_dir( project_dir )
        
        # Create docker folder and copy the docker folder -> project space folder
        docker_dir = project_dir + '/docker-standalone'
        self._create_dir( docker_dir )
        # Copy data to docker directory and remove the tmp directory
        if self._exists_dir( self.tmpDir ):
            self._copy_dir( self.tmpDir, docker_dir )
            self._remove_dir( self.tmpDir )
        
        # Get project information in json and trig format
        json_str = json.dumps(project.to_dict(), indent=5, sort_keys=True)
        trig_str = project.parse_trig() 
        
        # Save json string in current project space
        with open( project_dir + "/" + project_name + ".json", "w") as text_file:
            text_file.write(json_str)
        
        # Save trig string in current project space
        with open( project_dir + "/" + project_name + ".trig", "w") as text_file:
            text_file.write(trig_str)
        
        # Save trig string in docker folder
        with open( project_dir + "/docker-standalone/instance/Configuration/TriG/waves.trig", "w") as file:
            file.write(trig_str)
    
    """
        Get project space information
    """
    
    def get_list_project(self):
        """ Fetch list of project names
        
        The list of project name is the same as list of folder names inside the project space directory.
        
        Returns:
            project_name_list: List of project names
        """
        
        # Get the list of directory names
        project_name_list = self._list_dir_name( self.directory )
        
        # Remove tmp in the list of directory names since it's the name of temporal folder
        if 'tmp' in project_name_list:    
            project_name_list.remove('tmp')
        else:
            pass
        
        return project_name_list
    
    """
        Save uploaded files
    """
    
    def save_raw_source_file(self, file):
        """ Save raw source file at temp raw source data file folder 
        
        :param file: uploaded raw source file
        """
        
        filename = secure_filename(file.filename)
        file.save(self.tmpRawSourceDir + '/' + filename)
        
    def save_rdf_source_file(self, file):
        """ Save rdf source file at temp rdf source data file folder 

        :param file: uploaded rdf source file
        """
        
        filename = secure_filename(file.filename)
        file.save(self.tmpRdfSourceDir + '/' + filename)
    
    def save_static_feed_file(self, file):
        """ Save static feed file at temp static doc feed file folder 
        
        :param file: uploaded static document feed file
        """
        
        filename = secure_filename(file.filename)
        file.save(self.tmpStaticFeedDir + '/' + filename)

    def get_static_feed_filename(self):
        """ Get the filename of static feed file

        We use this function during the process of creating a new project.
        This is used when we want to set the configuration of static feed location

        :return: file name of static feed file
        """

        # Get all files inside the temp static feed directory
        files = os.listdir( self.tmpStaticFeedDir )

        # Mac OS has some files start with '.' like '.DStore'
        # That's not the file we need, we will remove them
        files = [file for file in files if not file.startswith('.')]

        # There is only one static feed file
        return files[0]

        
    """
        Workflow UI tags read and write from text file
    """
        
    def save_workflow_ui(self, workflow_ui, project_name):
        """ Save workflow ui in HTML tags format into a text file 
        
        :param workflow_ui: workflow structure in HTML tags in string format
        :param project_name: project name
        """
        
        with open( self.directory + "/" + project_name + "/workflow.txt", "w") as file:
            file.write(workflow_ui)
    
    def get_workflow_ui(self, project_name):
        """ Get workflow ui in HTML tags in string format from text file 
        
        The string will be send back to front-end to view the structure of workflow.
        
        :param project_name: Project name to fetch the workflow ui html tags in string
            
        :return: workflow_ui: HTML tags for workflow structure in string format
        """
        
        workflow_ui = ""
        
        # Read the file line by line
        with open( self.directory + "/" + project_name + "/workflow.txt", "r") as file:
            for line in file:
                if line.rstrip() != "":
                    workflow_ui = workflow_ui + line.replace("\n", "")
        
        return workflow_ui
    
    """
        Get project in Project, json or trig format
    """
    
    def get_project(self, project_name):
        """ Get project from project_name

        :param project_name: project_name of project to fetch
        :return: returned project in Project Model
        """
         
         # Get project as Python dictionary
        project_dict = self.get_project_as_dict(project_name)
        
        # Use project to parse from python dict -> Project
        project = Project()
        return project.parse_from_dict(project_dict)        
    
    def get_project_as_trig(self, project_name):
        """ Get the project trig as string

        :param project_name: project_name of project to fetch
        :return: returned project in trig strng format
        """
        
        trig = ""
        
        # Read the file line by line
        with open( self.directory + "/" + project_name + "/" + project_name + ".trig", "r") as file:
            for line in file:
                trig = trig + line
        
        return trig
    
    def get_project_as_dict(self, project_name):
        """ Get the project as python dict

        :param project_name: project_name of project to fetch
        :return: returned project in python dict format
        """
        
        json_str = ""
        
        with open( self.directory + "/" + project_name + "/" + project_name + ".json", "r") as file:
            json_str = "".join(file)
        
        project_dict = json.loads(json_str)
        
        return project_dict
    
    """
        Delete Project
    """
    
    def delete_project(self, project_name):
        """ Delete Project

        Delete project at waves project space local directory

        :param project_name: name of project to be deleted
        :return:
        """
        self._remove_dir( self.directory + '/' + project_name)
        
    # ====================================
    # Private functions
    # ====================================
    
    """
        Directory processing 
    """
    
    def _create_dir(self, directory):       
        """ Create Directory """     
        os.makedirs(directory)
        
    def _empty_dir(self, directory):
        """ Empty Directory """
        self._remove_dir(directory)
        self._create_dir(directory)
    
    def _remove_dir(self, directory):
        """ Remove directory and all its sub files and sub directories """
        if os.path.exists(directory):
            shutil.rmtree(directory)
            
    def _exists_dir(self, directory):
        """ Check if the directory exists """
        return os.path.exists(directory)
    
    def _copy_dir(self, src, dst):
        """ Copy folder from source to destination """
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, False, None)
            else:
                shutil.copy2(s, d)
                
    def _list_dir_name(self, parentDir):
        """ Get list of directory in parent directort  """
        name_list = []
        
        if os.path.isdir(parentDir):
            for name in os.listdir(parentDir):
                # For mac, there're some folders with name ".DStore."
                # Need to remove them..
                if not name.startswith('.') :
                    name_list.append(name) 
        
        return name_list