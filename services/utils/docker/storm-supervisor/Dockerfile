FROM phusion/baseimage

MAINTAINER li_ke@yahoo.com

# Install Java
RUN add-apt-repository ppa:webupd8team/java -y  && \
    apt-get update && \
    echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    apt-get --allow-unauthenticated install -y  oracle-java8-installer && \
    apt-get clean

# Install useful tools and Supervisord
RUN apt-get update && \
    apt-get install -y wget supervisor vim software-properties-common net-tools && \
    add-apt-repository main && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

RUN wget -q -O - http://mirrors.sonic.net/apache/storm/apache-storm-1.0.1/apache-storm-1.0.1.tar.gz | tar -xzf - -C /opt

ENV STORM_HOME /opt/apache-storm-1.0.1
RUN groupadd storm; useradd --gid storm --home-dir /home/storm --create-home --shell /bin/bash storm; chown -R storm:storm $STORM_HOME; mkdir /var/log/storm ; chown -R storm:storm /var/log/storm

RUN ln -s $STORM_HOME/bin/storm /usr/bin/storm

ADD storm.yaml $STORM_HOME/conf/storm.yaml
ADD cluster.xml $STORM_HOME/logback/cluster.xml
ADD config-supervisord.sh /usr/bin/config-supervisord.sh
ADD start-supervisor.sh /usr/bin/start-supervisor.sh
RUN chmod a+x /usr/bin/config-supervisord.sh
RUN chmod a+x /usr/bin/start-supervisor.sh

RUN echo [supervisord] | tee -a /etc/supervisor/supervisord.conf ; echo nodaemon=true | tee -a /etc/supervisor/supervisord.conf

RUN apt-get update && apt-get install make && apt-get install -y gcc 

# Install redis
RUN wget http://download.redis.io/releases/redis-3.0.5.tar.gz && \
    tar xzf redis-3.0.5.tar.gz && \
    mv redis-3.0.5 /usr/local/redis && \
    rm redis-3.0.5.tar.gz && \
    cd /usr/local/redis && \
    make 

RUN mkdir /usr/local/srcFolder
ADD srcFolder /usr/local/srcFolder

RUN /usr/bin/config-supervisord.sh supervisor
RUN /usr/bin/config-supervisord.sh logviewer

EXPOSE 6700
EXPOSE 6701
EXPOSE 6702
EXPOSE 6703
EXPOSE 8000
EXPOSE 6379
