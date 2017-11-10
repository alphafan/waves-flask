FROM phusion/baseimage
 
MAINTAINER li_ke@yahoo.com

# Environment
ENV TOMCAT_MAJOR_VERSION 9
ENV TOMCAT_VERSION 9.0.0
ENV TOMCAT_MINOR_VERSION 22
ENV SESAME_VERSION 2.8.11

# Upgrade Java to last version
RUN add-apt-repository ppa:webupd8team/java -y  && \
    apt-get update && \
    echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    apt-get --allow-unauthenticated install -y  oracle-java8-installer && \
    apt-get clean


# Download and install tomcat 
# change v9.0.0 with v_TOMCAT_VERSION, il will change the tomcat version automaticly
RUN wget -P /tmp http://archive.apache.org/dist/tomcat/tomcat-${TOMCAT_MAJOR_VERSION}/v${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}.tar.gz && \
    tar xfz /tmp/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}.tar.gz -C /opt && \
    rm /tmp/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}.tar.gz

# Configure Tomcat 
RUN groupadd tomcat && \
    useradd -s /bin/false -g tomcat -d /opt/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION} tomcat && \
    chown -R tomcat /opt/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION} 


# Install Sesame
RUN curl -sS -o /tmp/sesame.tar.gz -L http://sourceforge.net/projects/sesame/files/Sesame%202/$SESAME_VERSION/openrdf-sesame-${SESAME_VERSION}-sdk.tar.gz/download && \
    tar -xzf /tmp/sesame.tar.gz -C /opt && \ 
    ln -s /opt/openrdf-sesame-${SESAME_VERSION} /opt/sesame && \
    rm /tmp/sesame.tar.gz

# Deploy 
RUN mkdir /opt/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}/webapps/openrdf-sesame && \
    cd /opt/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}/webapps/openrdf-sesame && \
    jar xf /opt/sesame/war/openrdf-sesame.war && \
    mkdir /opt/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}/webapps/openrdf-workbench && \
    cd /opt/apache-tomcat-${TOMCAT_VERSION}.M${TOMCAT_MINOR_VERSION}/webapps/openrdf-workbench && \
    jar xf /opt/sesame/war/openrdf-workbench.war

RUN mkdir waves

EXPOSE 8080
