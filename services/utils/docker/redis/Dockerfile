FROM phusion/baseimage

MAINTAINER li_ke@yahoo.com

RUN apt-get update && apt-get install make && apt-get install -y gcc 

# Install Java
RUN add-apt-repository ppa:webupd8team/java -y  && \
    apt-get update && \
    echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    apt-get --allow-unauthenticated install -y  oracle-java8-installer && \
    apt-get clean
    
# Install redis
RUN wget http://download.redis.io/releases/redis-3.0.5.tar.gz && \
    tar xzf redis-3.0.5.tar.gz && \
    mv redis-3.0.5 /usr/local/redis && \
    rm redis-3.0.5.tar.gz && \
    cd /usr/local/redis && \
    make 

EXPOSE 6379
