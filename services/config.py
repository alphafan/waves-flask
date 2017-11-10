# -*- coding: utf-8 -*-

"""
    Docker deploying conf
    - dckLoc : is the path to the binary file of Docker
    - dckCmpsLoc : is the path to the binary file of docker compose

    Need to specify it for each server deployment to be setup like a default config

    this configuration can also modified to each container deployment if the deployment it is not global.
    this can be setup by using "Deploy Settings" in button of the UI
"""

class DeploySetting(object):
    
    dckLoc = "/usr/local/bin/docker"
    dckCmpsLoc = "/usr/local/bin/docker-compose"