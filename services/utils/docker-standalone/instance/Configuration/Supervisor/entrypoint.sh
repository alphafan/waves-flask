#!/bin/bash

echo "Starting Spark components"
/opt/apache-spark-2.1.0/sbin/start-all.sh &
bgPID1=$!
sleep 5
echo "Spark is ready !"

echo "Starting Tomcat..."
/opt/apache-tomcat-8.5.23/bin/startup.sh
sleep 10

echo "Creating Waves Sesame Repo ..."
printf 'connect http://localhost:8787/rdf4j-server\ncreate native\nwaves\nwaves\n10000\n \n\nexit\n' | /opt/eclipse-rdf4j-2.2.2/bin/console.sh
sleep 5
echo "Sesame is ready !"

echo "Shutting down Tomcat"
/opt/apache-tomcat-8.5.23/bin/shutdown.sh
sleep 5
            
# Use Supervisor to restart all processes 

    if [ "$1" = 'supervisor' ]; then
       exec /usr/bin/supervisord -n
    fi

exec "$@"
