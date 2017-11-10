# -*- coding: utf-8 -*-

""" Docker Handler deal with docker deployment related issues

This class is used for doing three things:
- Launch docker containers
- Stop   docker containers
- Remove docker containers

"""
import docker
import subprocess

from services.config import DeploySetting
from services.utils.FileHandler import FileHandler

class DockerHandler(object):
    
    def __init__(self):
        """ Initial functions
            
        Params:
            self.client   : The entry point for Docker Python API
            self.fhandler : File handler, we need this because we need to knwo the location of dockerfiles 
        """
        self.client = docker.from_env()
        self.fhandler = FileHandler()
        
    """
        Launch docker container
    """
        
    def docker_compose_up(self, project_name):
        """ Launch the docker container in standalone mode

        This method is used for current version (0.5), it has only one dockerfile in docker-compose.
        To launch the container in standalone mode,
        - 1, We will find the location of the project docker directory
        - 2, Run the command "docker-compose up -d" to launch container
        - 3, During the launching process, every time it has output from the execution of command,
             yield the output just like a session to the front end
        - 4, Yield a sentence as a flag to tell the front end to close the session

        :param project_name: Name of the project to be launched
        :return: yielding the execution result
        """
        
        # Location of project docker root path
        project_docker_dir = self.fhandler.directory + '/' + project_name + '/docker-standalone'
       
        # Command to build docker image
        # First param is the docker-compose installed ABSOLUTE location
        #     - We must give the absolute path of docker-compose, 
        #         if not, it will not find it
        # Second param is the project docker directort path
        #    - Just after the -f to specify the path
        command = """
            {} -f {}/docker-compose.yml up -d
        """.format( DeploySetting.dckCmpsLoc, project_docker_dir)
        
        # See how the command looks like
        print( command )
        
        # Run the command and yield the output of execution line by line
        for line in self._run_process(command.split()):
            yield line
        
        # Once finished, yield this sentence
        yield "Deploying process is finished"
        
    
    """
        Stop running containers
    """
    def docker_compose_stop(self, project_name):
        """ Stop the running container

        Almost the same steps as docker_compose_uo, we only need to replace the command -> stop
            1. Find the docker-compose file location
            2. Docker compose stop
            3, Yield stdouts
            4, Yield finished flag sentence

        :param project_name: Name of the project to be stoppped
        :return: yielding the execution result
        """
        
        # Project docker directory
        project_docker_dir = self.fhandler.directory + '/' + project_name + '/docker-standalone'
        
        # Command to stop
        command = """
            {} -f {}/docker-compose.yml stop
        """.format( DeploySetting.dckCmpsLoc, project_docker_dir)
        
        # Print out the command 
        print( command )
        
        # Yield every output 
        for line in self._run_process(command.split()):
            yield line
        
        # Yield the flag sentence
        yield "All containers have been stopped"

    """
        Stop running containers and delete them
    """
    def docker_compose_down(self, project_name):
        """ Stop and remove the running container

        Almost the same steps as docker_compose_uo, we only need to replace the command -> down
            1. Find the docker-compose file location
            2. Docker compose stop
            3, Yield stdouts
            4, Yield finished flag sentence

        :param project_name: Name of the project to be stopped and removed
        :return: yielding out the execution result
        """
        
        # Project docker directory
        project_dir = self.fhandler.directory + '/' + project_name + '/docker-standalone'
        
        # Command to stop and remove
        command = """
            {} -f {}/docker-compose.yml down
        """.format( DeploySetting.dckCmpsLoc, project_dir)
        
        # Print out the command 
        print( command )
        
        # Yield every output 
        for line in self._run_process(command.split()):
            yield line
        
        # Yield the flag sentence        
        yield "All containers have been removed"

    # ====================================
    # Private functions
    # ====================================
    
    def _get_container_by_name(self, container_name):
        """ Get the container from its name

        :param container_name: name of container to be obtained
        :return: If exist this container, return it, if not, return None
        """
        
        for container in self.client.containers.list():
            if container.name == container_name:
                return container
            
        return None
        
    def _run_process(self, command):
        """ Run command using subprocess.Popen

        :param command: command to run
        :return: yield every std output line
        """

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while(True):
            retcode = p.poll() #returns None while subprocess is running
            line = p.stdout.readline()
            yield line.decode('utf-8').rstrip() 
            if(retcode is not None):
                break