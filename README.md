# Waves Configurator

Waves Configurator aims to provide a GUI for Waves users to build, manage and execute Distributed RDF Stream Processing project in Waves Platform. It is built upon a Python Flasky Server which is in charge of creating project and semantise the configuration into a TriG file.( Each project will be represented as a RDF Graph with one Graph URI Idetifier generated from project name. ) 

In the Front-end part, we rely on Bootstrap UI Framwork, jQuery, jQuery-ui and jsPlumb to build the interface. 
* Bootstrap is used for designing the web
* jQuery is mainly in charge of the communication with server sides by sending RESTful requests
* jQuery-ui and jsPlumb is to enable the dragging, dropping and interconnections for interactively set up a project.

In the Back-end, we use Python as server for the following roles:
* Parse the project as a TriG
* Manage Docker containers by Docker Engine API
    * Start Docker containers with docker-compose up -d
    * Stop / Remove containers 
    * Upload datasets into specific docker container
    * Run command in docker containers to launch Waves Program

## Pre-requirements for running the program.
* Python 3.x ( In preference 3.6 + ) 
    * It is recommended to download an Anaconda Python IDE. Well, it's optional. But Anaconda is really strong because several good IDE like Spyder is already included and many commom libraries have already been installed.
* pip tools (Used for install some external python libraries)
    * If you have Anaconda installed, normally pip is installed as well which means that you don't need to install it manually.

However, you can still check if you have aleardy installed these two tools (Python 3.x and pip) by typing the following commands:
```
python --version
```
```
pip --version
```
Once it's done, you can start install the dependencies for this project by pip.
```
pip install flask docker rdflib validators
```
* Docker (Used to for providing the container based distributed enviornment)
    * You need to have Docker and Docker Compose installed in your local machine. https://docs.docker.com/engine/installation/ is the link for guiding you how to install Docker. https://docs.docker.com/compose/install/ will help install Docker Compose.

Once all above have been finished. You could start running the project now.

## Luanch the program
Go to project folder and run command 
```
python main.py
```
Launch your favorite browser and type http://localhost:5000 . Enjoy !!

## Screenshots
### Welcome Page :
![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/1%20Welcome.png)

### Create Project :
![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/2%20Step%201.png)

![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/3%20Step%202%20workflow.png)

![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/4%20Step%202%20settings.png)

![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/5%20Step%203%20submit.png)

![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/6%20View%20Trig.png)

### Project Space :
![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/7%20Project%20Space.png)

### Project Details :
![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/8%20Project%20details%20-1.png)

### Launch Project :
![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/11%20Launch%20containers.png)

![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/13%20Launch%20program.png)

![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/14%20Supervision.png)

### Storm UI:
![alt text](https://github.com/YufanZheng/waves-flask/blob/master/screenshots/15%20Storm%20UI.png)

