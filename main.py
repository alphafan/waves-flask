# -*- coding: utf-8 -*-

"""Flask Application Entry Module

This module is the entry point of launching the program.
We choose Python Flask Web Framework to support the back-end.

This program contains several modules:
    * Create project
        * add    component
        * remove component
        * update component location
        * save   component settings
        * get    component settings
        * add    link
        * remove link
        * save   link settings
        * upload file
        * upload multi file
        * save   clock settings
        * save   clock settings standalone
        * preview trig
    * Delete project
        * delete project
    * Modify project
        * modify project
    * Launch project
        * launch containers
        * stop   containers
        * remove containers
    * Project details
        * load project component settings

To launch the program:

        $ python main.py

"""

from flask import Flask, request, Response, send_from_directory
from flask import render_template
app = Flask(__name__, static_url_path='/static')

import json
from datetime import datetime
import validators
from werkzeug.utils import secure_filename

from services.model import Project, ProjectInfo, Workflow, Component, ClusterInfo, Metrics, Clock
from services.utils import FileHandler, DockerHandler
from services.config import DeploySetting

# ========================================
#   Handle Static Files
# ========================================

@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/static/js/myscripts/<path:path>')
def send_my_js(path):
    return send_from_directory('static/js/myscripts', path)

@app.route('/static/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/static/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('static/fonts', path)

@app.route('/static/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)

@app.route('/static/img/workflow/<path:path>')
def send_workflow_img(path):
    return send_from_directory('static/img/workflow', path)

# ========================================
#   Global Variables
# ========================================

"""
    Global variables to save the settings info during the creation & modification of a project
        - When load the create-project / modify-project page, init these global variables
        - Every time a new component / link is added or the settings of component is added,
            the value in each global variable will be modified
    
    Global Args: 
        projectInfo : Contains the information of installation: project name, description etc.
        clusterInfo : Information about the hosts and IPs 
        workflow    : 
            - List of components
            - List of links
        metrics     : Monitoring parameters
        clock       : Acceleration parameters
        cmptCounter : Number of current added components, used for automatic setting the id
"""

projectInfo = ProjectInfo()
clusterInfo = ClusterInfo()
workflow    = Workflow()
metrics     = Metrics()
clock       = Clock()

cmptCounter = 0


# ========================================
#   Welcome Page
# ========================================


"""
    Load Welcome Page
"""

@app.route('/')
def load_index():
    """ Load Welcome page
    
    When launch the program, http://localhost:9002/ -> index.html
    """
    return render_template('index.html')


# ========================================
#   About Page
# ========================================


"""
    Load About Page
"""


@app.route('/about')
def load_about():
    """ Load About page """
    return render_template('about.html')


# ========================================
#   Create Project Related
# ========================================


"""
    Load Create Project Page
"""

@app.route('/create-project', methods=['GET'])
def load_create_project():
    """ Load Page to create a project
    
    When launch the program, http://localhost:9002/create-project -> show page create-project.html
    There are 2 steps to do when load this page
    
    Step 1: Init all global variables when load this page, make sure that:
        - List of components in workflow is empty
        - List of links      in workflow is empty
        - Number of components is 0
    
    Step 2: Set up project folder
        - If /{user.home}/Documents/waves_project_space folder doesn't exist, create the folder
        - Create a tmp folder for temporal saving the uploaded files,
            the temporal files will be moved the project folder once user clicked submit project button
        - Copy the docker-standalone folder into tmp folder,
            when user submit the project, it will also be moved to project folder
            to be used for building the Docker image and containers
    """
    
    # Initial global variables
    global workflow, clock, cmptCounter
    workflow.cmpt_list = []
    workflow.link_list = []
    cmptCounter = 0
    
    # Init Project Space folder 
    handler = FileHandler()
    handler.setup_project_space_folder()
    
    return render_template('create-project.html', clock=clock)

"""
    Final step : assembly All Project Information and Create Project
"""

# Receive form data and create a project
@app.route('/create-project', methods=['POST'])
def create_project():
    """When user clicked on the button, retrieve the project information and build the project
    
    Project information contains 5 parts: 
        - ProjectInfo  : Information is obtained from the submitted form data
        - ClusterInfo  : Use default cluster IP and host information
        - Workflow     : 
            Workflow information is updated while adding, removing, save settings
                of the components etc.
            The information is already saved in workflow global variable, 
                no need to retrieve from the form data
        - Metrics     : Information is obtained from the submitted form data
        - Clock       : Information already saved in global variable clock 
                when user click on the button of saving clock settings
    
     Step 1: Retrieve project information
         - Get global project information from form data
         - Use default cluster information
         - Use already updated workflow components and links information
         - Get metrics information form form data
         - Use already updated clock information
    
     Step 2: Save workflow UI
         - The workflow_ui is the HTML tags '<div>...</div>' which saves the UI level's 
             workflow structure
         - When view the details of project (the workflow structure, cmpt settings etc.)
             The front end will load the workflow_ui from back end and replace with 
             the empty workflow space.
    
     Step 3: Parse the project information into TriG
     
     Step 4: Set up project folder
         - New a folder with the name of project name at /{user.root}/Documents/waves_project_space/
         - Generate TriG file and put it into docker configuration folder
         - Put all docker folder, srcFiles, srcFolder into the project folder
         - Save the workflow_ui HTML tags into a file
    
     Notes: 
         - Saving the HTML tags is a compromised solution. I have to admit that re-draw the 
             workflow according to their saved locations and settings is the best solution. 
             However, the jsPlumb API always has some bugs when re-drawing the workflow i.e.:
                 - The connection points are not correct. 
                     Source point starts from the top-left of screen but not component
                 - Can not dragging a link from re-drawwed component
                 - etc.
         - To remedy this problem, I have to save the HTML tags. When repaint the workflow, just 
             replace it.
         - When user want to modify the project, it has to re-create the project and can not modify
             directly on the existing workflow.
    """
    
    global projectInfo, clusterInfo, workflow, metrics, clock
    
    print(request.form)
    
    # Receive form data
    projectInfo.name = request.form['name']
    projectInfo.description = request.form['description']
    projectInfo.license = request.form['license']
    projectInfo.version = request.form['version']
    projectInfo.createdAt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    metrics.frequency = request.form['frequency']
    metrics.reporters = request.form['reporters']
    
    workflow_ui = request.form['workflow_ui']
    
    # Create a new project
    project = Project(projectInfo, clusterInfo, workflow, metrics, clock)
    
    # Parse project -> TriG
    resp = {}
    resp['trig'] = project.parse_trig() 
    
    # Create the project folder
    handler = FileHandler()
    handler.setup_project_folder(project)
    handler.save_workflow_ui(workflow_ui, projectInfo.name)
    
    return json.dumps(resp)

"""
    Add Component in Workflow
"""

@app.route('/create-project/add-component', methods=['POST'])
def add_component():
    """ Add component in workflow
    
    When user drag a component from selector and drop it -> workflow space. The function here 
    will be triggered. 
    
    Example of component:
        - cmptType : RawSource
        - id       : jsPlumb_2_1   # HTML tag ID
        - ui_left  : 87px
        - ui_top   : 132px
        - settings : {
            'id' : 1,              # ID in TriG file
            /* Other settings */
        }  
    """
    
    # Get basic component settings
    cmpt = Component()
    cmpt.cmptType = request.form['cmptType'] 
    cmpt.id = request.form['id'] 
    cmpt.ui_left = request.form['ui_left'] 
    cmpt.ui_top = request.form['ui_top'] 
    
    # Automatically append id
    global cmptCounter
    settings = {}
    cmptCounter = cmptCounter + 1
    settings["id"] = str(cmptCounter)
    cmpt.settings = settings
       
    # Append component to workflow component list
    global workflow
    workflow.add_cmpt( cmpt )
    
    return '{}'

"""
    Remove Component from Workflow
"""

@app.route('/create-project/remove-component', methods=['POST'])
def remove_component():
    """ Remove component from Workflow
    
    - Remove all links that are related to the component, source link or target link
    - Remove component from workflow component list
    """
    global workflow
    cmptId = request.form['id']
    workflow.del_all_links(cmptId)
    workflow.del_cmpt_by_id(cmptId)

    return '{}'

"""
    Update Component's UI location in Workflow
"""

@app.route('/create-project/update-component-location', methods=['POST'])
def update_component_location():
    """ Update Component's UI Location when user drag and drop component """
    
    global workflow
    workflow.update_component_location(
            request.form['id'], 
            request.form['ui_left'],
            request.form['ui_top'])
    
    return '{}'

"""
    Save component's settings
"""

@app.route('/create-project/save-component-settings', methods=['POST'])
def save_component_settings():
    """ Save component settings when user click on 'Save Settings' button.
    
    Retrieve from key-value form data and set the component settings
    The component's settings is in fact a python dictionary.
    
    For some special keys, we will make some modifications
        - cmpt_id : do not need to save it in settings, so pass it
        - location : Since we deploy the program at container, the location should be 
                the location at the container.
            Check if the location is URL or filename, if it's not a url location:
                If raw source, make the location as "/usr/local/srcFolder/"
                If others, "/usr/local/srcFiles/" + filename
        - outputFile : Add prefix of "/usr/local/" 
        - inputFolder : Add prefix of '/usr/local/srcFolder'
        
    Set component settings.
    """
    global workflow
    cmpt_id = request.form['cmpt_id']
    cmpt_type = request.form['cmpt_type']
    print(request.form)
    
    cmpt = workflow.get_cmpt_by_id(cmpt_id)
    
    settings = {}
    settings['id'] = cmpt.settings['id']
    
    for key, value in request.form.items():

        # Do not save the component id
        if key != 'cmpt_id':
            settings[key] = value

        # RawSource data location in docker
        if cmpt_type == 'RawSource' and key == 'location':
            # Check if it's url
            # If it's not a url, means that it's a file source
            if validators.url(value) != True:
                # Save the location as the folder path in docker container
                settings[key] = "/opt/data/csv"

        # RdfSource data location in docker
        if cmpt_type == 'Source' and key == 'inputFolder':
            # Check if it's url
            # If it's not a url, means that it's a file source
            if validators.url(value) != True:
                # Save the location as the folder path in docker container
                settings[key] = "/opt/data/rdfSource"

        # Static Feed data location in docker
        if cmpt_type == 'RdfFeed' and key == 'location':
            fhandler = FileHandler()
            settings[key] = "/opt/data/rdf/" + fhandler.get_static_feed_filename()

        # Sink Location
        if cmpt_type == 'Sink' and key == 'outputFile':
            settings[key] = value.split('\\')[-1]

    workflow.save_component_settings(cmpt_id, settings)
    
    return '{}'

"""
    Get Component Settings
"""

@app.route('/create-project/get-component-settings', methods=['POST'])
def get_component_settings():
    """ When user click on component in workflow space, load the component settings """
    
    global workflow
    cmpt = workflow.get_cmpt_by_id(request.form['id'])
    if cmpt != None:
        settings = cmpt.settings
        return json.dumps(settings)
    else:
        return '{}'

"""
    Add component link
"""

@app.route('/create-project/add-link', methods=['POST'])
def add_link():
    """ Add component link by giving source component id and target component id """
    
    global workflow 
    workflow.add_link_with_cmpt_ids(
            request.form['srcCmptId'],
            request.form['trgCmptId'])
    
    return '{}'

"""
    Remove link
"""

@app.route('/create-project/remove-link', methods=['POST'])
def remove_link():
    """ Remove link """
    
    global workflow 
    workflow.del_link_by_src_cmpt_id(
            request.form['srcCmptId'])
    
    return '{}'

"""
    Save link settings
"""

@app.route('/create-project/save-link-settings', methods=['POST'])
def save_link_settings():
    """ Save Link Settings
    
    This is only used for window span settings between RDF stream and Semantic Filter
    """
    
    global workflow 
    settings = {}

    for key, value in request.form.items():
        # if key == "windowSpan":
        if key != 'srcCmptId' and key != "trgCmptId":
            settings[key] = value

    workflow.save_link_settings_by_cmpt_ids(
            request.form['srcCmptId'],
            request.form['trgCmptId'],
            settings)
    
    return '{}'

"""
    Load default workflow
"""

@app.route('/create-project/default-workflow', methods=['POST'])
def get_default_workflow():
    global workflow
    workflow.cmpt_list = []
    workflow.link_list = []
    
    default_workflow = workflow.get_default_workflow()
    return default_workflow

# ========================================
#   Upload File
# ========================================

"""
    Upload Single File
"""

@app.route('/create-project/upload-single-file', methods=['POST'])
def upload_single_file():
    """ Upload single files 

    This method is used for static feed
    The file will be saved at tmp folder at /{user.home}/Documents/waves_project_space/tmp/Data/StaticFeed
    """
    handler = FileHandler()
    files = request.files.getlist("location")

    if len(files) == 1:
        file = files[0]
        handler.save_static_feed_file(file)
    return '{}'

"""
    Upload Multi Files
"""

@app.route('/create-project/upload-multi-file', methods=['POST'])
def upload_multi_files():
    """ Upload Multi File

    The name of input may be location or inputFolder, need to retrieve them independently.
    For raw source, the name is location
    For rdf source, the name is inputFolder
    """
    handler = FileHandler()
    
    if request.files.getlist("inputFolder") == []:
        # If not inputFolder, uploaded file -> raw source
        files = request.files.getlist("location")
        for file in files:
            handler.save_raw_source_file(file)
    else:
        # Files are for rdf source
        files = request.files.getlist("inputFolder")
        for file in files:
            handler.save_rdf_source_file(file)

    return '{}'

"""
    Save deploy settings
"""

@app.route('/launch-program/save-deploy-settings', methods=['POST'])
def save_deploy_settings():

    """ Deploy settings
    
    Specify the docker and docker compose installed location 
    """
    DeploySetting.dckLoc = request.form['dckLoc']
    DeploySetting.dckCmpsLoc = request.form['dckCmpsLoc']
    
    print(DeploySetting.dckLoc)
    
    return '{}'

"""
    Save clock settings
"""

@app.route('/create-project/save-clock-settings', methods=['POST'])
def save_clock_settings():
    
    """ Save clock settings by choosing two modes
    
    Mode 1: Use startTime, acceleration
    Mode 2: Use startTime, endTime, duration
    """
    
    global clock
    if "acceleration" in request.form:
        clock.startDate = request.form['startDate']
        clock.acceleration = request.form['acceleration']
        clock.localTimeZone = request.form['localTimeZone']
    else:
        clock.startDate = request.form['startDate']
        clock.endDate = request.form['endDate']
        clock.duration = request.form['duration']
        clock.localTimeZone = request.form['localTimeZone']
    
    return '{}'

"""
    Preview TriG
"""

@app.route('/create-project/preview-trig', methods=['POST'])
def preview_trig():
    
    """ Retrieve project information and generate TriG """
    
    global projectInfo, clusterInfo, workflow, metrics, clock

    projectInfo.name = request.form['name']
    projectInfo.description = request.form['description']
    projectInfo.license = request.form['license']
    projectInfo.version = request.form['version']
    projectInfo.createdAt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    metrics.frequency = request.form['frequency']
    metrics.reporters = request.form['reporters']
    
    project = Project(projectInfo, clusterInfo, workflow, metrics, clock)
    
    resp = {}
    resp['trig'] = project.parse_trig() 
    
    print( json.dumps(project.to_dict(), indent=5, sort_keys=True) )
    
    return json.dumps(resp)

"""
    Delete Project
"""

@app.route('/delete-project', methods=['POST'])
def delete_project():
    """ Delete project """

    pname = request.form['name']
    
    handler = FileHandler()
    handler.delete_project(pname)
    
    return "{}"

"""
    Load Project Space Page
"""

@app.route('/project-space')
def load_project_space():
    """ Load Project Space
        
    Read all project names from project space local folder /{user.home}/Documents/waves_project_space
    The project names are the list of folder names
    """
    handler = FileHandler()
    pnames = handler.get_list_project()
    projects = []
    for pname in pnames:
        project = handler.get_project_as_dict(pname)
        projects.append(project)
    return render_template('project-space.html', projects=projects)

"""
    Load Project Details Page
"""

@app.route('/project-space/<name>/details')
def load_project_details(name):
    """ Load the details of project

    :param name: name of the project
    :return:
    """
    handler = FileHandler()
    # Load project information as json for processingin UI
    project = handler.get_project_as_dict(name)
    workflow_ui = handler.get_workflow_ui(name).rstrip()
    trig = handler.get_project_as_trig(name)
    return render_template('project-details.html', project=project, workflow_ui=workflow_ui, trig=trig)

"""
    Load project component settings
"""

@app.route('/project-space/<name>/details/get-component-settings', methods=['POST'])
def load_project_component_settings(name):
    """ Get the project all component's settings

    :param name: name of the project
    :return: Json format of the all the components settings
    """
    handler = FileHandler()
    project = handler.get_project_as_dict(name)
    
    cmpt_id = request.form['id']
    cmpt_list = project['workflow']['cmpt_list']
    
    settings = {}
    
    for cmpt in cmpt_list:
        if cmpt['id'] == cmpt_id:
            settings = cmpt['settings']
    
    return json.dumps(settings)

# ========================================
#   Docker deployement
# ========================================

"""
    Load launch program page
"""

@app.route('/launch-program/<name>')
def load_launch_program_page(name):
    """ Load launch program page

    :param name: name of the project to be launched
    :return:
    """
    print("to launch program", name)
    return render_template('launch-program.html', Config=DeploySetting)

"""
    Launch containers
"""

@app.route('/launch-program/<name>/launch-containers')
def launch_containers(name):
    """ Launch the project's docker container

    :param name: name of the project
    :return:
    """
    
    print("to launch containers", name)
    
    client = DockerHandler()
    
    # Run docker in standalone mode
    return Response(
        stream( client.docker_compose_up, name ),
        mimetype='text/event-stream')
    
"""
    Stop containers
"""

@app.route('/launch-program/<name>/stop-containers')
def stop_containers(name):
    """ Stop running container

    :param name: name of the project to be stopped
    :return:
    """
    
    print("to stop containers", name)
    
    client = DockerHandler()
    
    return Response(
        stream( client.docker_compose_stop, name ),
        mimetype='text/event-stream')
   
"""
    Stop and delete containers
"""
 
@app.route('/launch-program/<name>/delete-containers')
def delete_containers(name):
    """ Stop and delete the docker containers

    :param name: name of the project
    :return:
    """
    print("to delete containers", name)
    
    client = DockerHandler()
    
    return Response(
        stream( client.docker_compose_down, name ),
        mimetype='text/event-stream')

"""
    Modify the project
"""

@app.route('/modify-project/<name>')
def modify_project(name):
    """ Modify the project

    :param name: name of the project to be modified
    :return:
    """
    
    handler = FileHandler()
    
    project = handler.get_project(name)
    
    global projectInfo, clusterInfo, workflow, metrics, clock
    
    # Modify the project by re-create workflow
    projectInfo = project.projectInfo
    clusterInfo = project.clusterInfo
    workflow = Workflow()
    metrics = project.metrics
    clock = project.clock
    
    return render_template('modify-project.html', project=project, clock=clock)

"""
    Streaming out the results
"""

# Stream the python yield result
def stream(methodToRun, project_name):
    """ Streaming out the result of yield to front end

    There're several streaming method like, docker-compose up/stop/down.

    :param methodToRun: streaming method
    :param project_name: name of the project
    :return:
    """
    for line in methodToRun(project_name) :
        yield """
            retry: 10000\ndata:{"time":"%s", "message":%s}\n\n
        """ % ( datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        '"{}"'.format( line.rstrip() ))


"""
    Launch APP
"""

if __name__ == '__main__':
    app.run(debug=True, port=9002)