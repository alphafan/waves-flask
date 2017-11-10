# OS base for the container
FROM phusion/baseimage

# Maintenance of the dockerfile
MAINTAINER Badre Belabbess <badre.belabbess@tos.net>

# Software versions
ENV JAVA_VERSION 1.8
ENV SCALA_VERSION 2.11
ENV ZK_VERSION 3.4.9
ENV SBT_VERSION 0.13.0
ENV KAFKA_VERSION 0.9.0.1
ENV REDIS_VERSION 4.0.2
ENV INFLUXDB_VERSION 1.1.1
ENV SPARK_VERSION 2.1.0
ENV HADOOP_VERSION 2.7
ENV TOMCAT_VERSION 8.5.23
ENV SESAME_VERSION 2.2.2

ENV HOME /opt
WORKDIR $HOME

# Destination folders
ENV ZK_HOME /opt/zookeeper-$ZK_VERSION
ENV KAFKA_HOME /opt/kafka-$SCALA_VERSION-$KAFKA_VERSION
ENV SPARK_HOME /opt/apache-spark-$SPARK_VERSION
ENV REDIS_HOME /opt/redis-$REDIS_VERSION
ENV INFLUXDB_HOME /opt/redis-$INFLUXDB_VERSION
ENV SESAME_HOME /opt/

# Useful tools for managing the container & the application
RUN apt-get update && \
    apt-get install -y wget maven make gcc logrotate supervisor zip vim software-properties-common net-tools dos2unix && \
    add-apt-repository main && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Configure Supervisor to display web interface
RUN rm /etc/supervisor/supervisord.conf
ADD Configuration/Supervisor/supervisord.conf /etc/supervisor/


# Upgrade Java to last version
RUN rm -rf java-8-openjdk-amd64 && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:webupd8team/java -y && \
    apt-get update -y &&\
    apt-get install -y default-jre &&\
    apt-get install -y default-jdk

# Install Scala 
RUN wget --no-check-certificate -P /tmp https://downloads.typesafe.com/scala/${SCALA_VERSION}.11/scala-${SCALA_VERSION}.11.tgz && \
    tar xfz /tmp/scala-${SCALA_VERSION}.11.tgz  -C /opt && \
    rm /tmp/scala-${SCALA_VERSION}.11.tgz

# Install SBT 
RUN echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823 && \
    apt-get update -y && \
    apt-get install -y sbt

# Install Zookeeper
RUN wget --no-check-certificate -P /tmp http://apache.mirrors.ovh.net/ftp.apache.org/dist/zookeeper/zookeeper-$ZK_VERSION/zookeeper-$ZK_VERSION.tar.gz && \
tar xfz /tmp/zookeeper-$ZK_VERSION.tar.gz -C /opt && \
rm /tmp/zookeeper-$ZK_VERSION.tar.gz

# Configure Zookeeper
RUN cp $ZK_HOME/conf/zoo_sample.cfg $ZK_HOME/conf/zoo.cfg

# Run Zookeper under supervision
RUN mkdir /var/log/zookeeper
ADD Configuration/Supervisor/zookeeper.conf /etc/supervisor/conf.d/

# Install Kafka
RUN wget --no-check-certificate -P /tmp  http://apache.crihan.fr/dist/kafka/$KAFKA_VERSION/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz  && \
    tar xfz /tmp/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz -C /opt && \
    rm /tmp/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz && \
    rm /opt/kafka_2.11-0.9.0.1/config/server.properties

ADD Configuration/Kafka/server.properties /opt/kafka_2.11-0.9.0.1/config/

# Run Kafka under supervision
RUN mkdir /var/log/kafka
ADD Configuration/Supervisor/kafka.conf  /etc/supervisor/conf.d

# Install KafkaDrop tool to monitor Kakfa topics and messages
RUN wget --no-check-certificate -P /tmp https://github.com/HomeAdvisor/Kafdrop/archive/master.zip && \
unzip /tmp/master.zip -d /opt && \
rm /tmp/master.zip && \
cd /opt/Kafdrop-master && \
mvn clean clean package

# Put KafkaDrop under Supervision
RUN mkdir /var/log/kafka-drop && \
    chmod 755 /opt/Kafdrop-master/target/kafdrop-2.0.0.jar
ADD Configuration/Supervisor/kafka-drop.conf /etc/supervisor/conf.d

# Install Redis
RUN wget --no-check-certificate -P /tmp http://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz && \
    tar -xzvf /tmp/redis-$REDIS_VERSION.tar.gz -C /opt && \
    cd /opt/redis-$REDIS_VERSION && \
    make

# Put Redis under supervision
RUN mkdir /var/log/redis
ADD Configuration/Supervisor/redis.conf /etc/supervisor/conf.d/

# Install InfluxDb
RUN wget --no-check-certificate -P /tmp  https://dl.influxdata.com/influxdb/releases/influxdb-1.1.1_linux_amd64.tar.gz && \
    tar xfz /tmp/influxdb-1.1.1_linux_amd64.tar.gz -C /opt && \
    rm /tmp/influxdb-1.1.1_linux_amd64.tar.gz

# Change InfluxDb configuration file
RUN mkdir /var/log/influxdb
ADD Configuration/InfluxDb/influx-waves.conf /opt/influxdb-1.1.1-1/etc/influxdb/

# Put Influx under supervision
ADD Configuration/Supervisor/influxdb.conf /etc/supervisor/conf.d/

# Install Tomcat
RUN wget --no-check-certificate -P /tmp http://apache.mindstudios.com/tomcat/tomcat-8/v8.5.23/bin/apache-tomcat-$TOMCAT_VERSION.tar.gz && \
    tar xfz /tmp/apache-tomcat-$TOMCAT_VERSION.tar.gz -C /opt && \
    groupadd tomcat && \
    useradd -s /bin/false -g tomcat -d /opt/apache-tomcat-$TOMCAT_VERSION tomcat && \
    chgrp -R tomcat /opt/apache-tomcat-$TOMCAT_VERSION && \
    chmod -R g+r /opt/apache-tomcat-$TOMCAT_VERSION/conf && \
    chmod g+x /opt/apache-tomcat-$TOMCAT_VERSION/conf && \
    chown -R tomcat /opt/apache-tomcat-$TOMCAT_VERSION/webapps  /opt/apache-tomcat-$TOMCAT_VERSION/work  /opt/apache-tomcat-$TOMCAT_VERSION/temp  /opt/apache-tomcat-$TOMCAT_VERSION/logs

# Configure Tomcat
RUN rm /opt/apache-tomcat-$TOMCAT_VERSION/conf/server.xml
ADD Configuration/Tomcat/server/server.xml /opt/apache-tomcat-$TOMCAT_VERSION/conf 


# Install Sesame and put it under Tomcat
RUN wget --no-check-certificate -P /tmp http://ftp-stud.fht-esslingen.de/pub/Mirrors/eclipse/rdf4j/eclipse-rdf4j-$SESAME_VERSION-sdk.zip && \
    unzip /tmp/eclipse-rdf4j-$SESAME_VERSION-sdk.zip -d /opt && \
    rm /tmp/eclipse-rdf4j-$SESAME_VERSION-sdk.zip && \
    cp /opt/eclipse-rdf4j-$SESAME_VERSION/war/* /opt/apache-tomcat-$TOMCAT_VERSION/webapps

# Put Tomcat under Supervision
RUN mkdir /var/log/tomcat
ADD Configuration/Supervisor/tomcat.conf /etc/supervisor/conf.d/

# Install Spark
RUN wget --no-check-certificate -P /tmp http://d3kbcqa49mib13.cloudfront.net/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar xfz /tmp/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /opt && \
    rm /tmp/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    cd /opt && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} apache-spark-2.1.0

# Put Spark under supervision (right now not working, so I used a direct script to launch it)
RUN mkdir /var/log/spark
#    echo "$(tail -n +2 /etc/hosts)" > /etc/hosts
#ADD Configuration/Supervisor/spark-master.conf /etc/supervisor/conf.d/
#ADD Configuration/Supervisor/spark-worker.conf /etc/supervisor/conf.d/

# Add needed Jars for the streaming application on spark
RUN mkdir /opt/jars && \
    mkdir /opt/jars/strider && \
    mkdir /opt/jars/waves

# Add Waves Jar that contains Waves Launcher
ADD Resources/WavesLauncher/waves-launcher-0.2.0-SNAPSHOT-shaded.jar /opt/jars/waves
RUN chmod 755 /opt/jars/waves/waves-launcher-0.2.0-SNAPSHOT-shaded.jar
ADD Resources/WavesLauncher/waves.trig  /opt/jars/waves

# Put Waves Launcher under supervision
ADD Resources/WavesLauncher/launch.sh  /opt/jars/waves
RUN mkdir /var/log/waves-launcher && \
    chmod 755 /opt/jars/waves/launch.sh && \
    dos2unix /opt/jars/waves/launch.sh
ADD Configuration/Supervisor/waves.conf /etc/supervisor/conf.d

# Add Strider Jar 
ADD Resources/StriderMain/strider-waves-test.jar /opt/jars/strider
ADD Resources/StriderMain/waves.trig /opt/jars/strider
ADD Resources/StriderMain/staticData.nt /opt/jars/strider
ADD Resources/StriderMain/tripleStoreData.nt /opt/jars/strider

# Put Strider under supervision
RUN mkdir /var/log/strider
ADD Configuration/Supervisor/strider.conf /etc/supervisor/conf.d

# Configure environment variables
ENV PATH $HOME/scala/bin:$HOME/sbt/bin:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH

# Add data for the run
RUN mkdir /opt/data
ADD Data/RawSource/ /opt/data/csv
ADD Data/RdfSource/ /opt/data/rdf

# Launch Spark using a shell Script because supervision does not work
ADD Configuration/Supervisor/entrypoint.sh /opt

# Expose ports for each application 
EXPOSE 2181 9092 9001 9000 6379 8086 8083 8088 8080 8042 4040 7077 8787

# Launch all components using Supervisor
ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["supervisor"]