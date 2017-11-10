# storm-docker

```
docker-compose up -d
```
containers' IPs:
zookeeper :        172.17.0.2<br/>
kafka :            172.17.0.3<br/>
tomcat(sesame) :   172.17.0.4<br/>
storm-nimbus :     172.17.0.5<br/>
storm-supervisor : 172.17.0.6<br/>
storm-ui :         172.17.0.7<br/>

start redis
```
docker exec -it docker_supervisor_1 /usr/local/redis/src/redis-server --daemonize yes
```
execute the application on storm
```
docker exec -it docker_nimbus_1 storm jar usr/local/waves-storm-0.2.0-SNAPSHOT.jar org.waves_rsp.storm.WavesTopology usr/local/test-topology.trig F-3f
```
visit sesame from storm nimbus
```
docker exec -it docker_nimbus_1 curl http://172.17.0.4:8080

docker exec -it docker_nimbus_1 curl http://172.17.0.4:8080/openrdf-workbench/repositories/waves/export
```
sesame page: http://localhost:8080/openrdf-workbench<br/>
storm UI: http://localhost:49080

