from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import XSD, RDFS
from decimal import Decimal

from services.model.ProjectInfo import ProjectInfo
from services.model.ClusterInfo import ClusterInfo
from services.model.Workflow import Workflow
from services.model.Metrics import Metrics
from services.model.Clock import Clock

class Project(object):
    
    def __init__(self, projectInfo=None, clusterInfo=None, 
                 workflow=None, metrics=None, clock=None):
        self.projectInfo = projectInfo
        self.clusterInfo = clusterInfo
        self.workflow    = workflow
        self.metrics     = metrics
        self.clock       = clock
    
    def to_dict(self):
        
        """ Parse information -> python dictionary

        :return: python dictionary which contains the information of model
        """
        
        info = {}
        
        info['projectInfo'] = self.projectInfo.to_dict()
        info['clusterInfo'] = self.clusterInfo.to_dict()
        info['workflow']    = self.workflow.to_dict()
        info['metrics']     = self.metrics.to_dict()
        info['clock']       = self.clock.to_dict()
        
        return info
    
    def parse_from_dict(self, info):
        """ From python dictionary fetch information and build this object

        :param info: python dictionary that contains the key-value format of the object
        :return: Object that contains the information of json
        """
        
        project = Project()
        
        projectInfo = ProjectInfo()
        clusterInfo = ClusterInfo()
        workflow    = Workflow()
        metrics     = Metrics()
        clock       = Clock()
        
        project.projectInfo = projectInfo.parse_from_dict( info['projectInfo'] )
        project.clusterInfo = clusterInfo.parse_from_dict( info['clusterInfo'] )
        project.workflow    = workflow   .parse_from_dict( info['workflow']    )
        project.metrics     = metrics    .parse_from_dict( info['metrics']     )
        project.clock       = clock      .parse_from_dict( info['clock']       )
        
        return project
    
    def parse_trig(self):
        # Init a graph
        g = Graph()
        
        # Handle Namespaces
        waves = Namespace("http://www.waves-rsp.org/configuration#")
        
        waves_str = "http://www.waves-rsp.org/configuration#"
        base_str = "http://localhost:9091/waves/" + self.projectInfo.name + "/"
        
        g.bind('waves', waves_str)
        
        # SETP 1: Parse project info
        """
            Output like :
            #Installation Global Settings
              <installation>
                rdf:type                waves:Installation ;
                waves:name              "projectName" ;
                ..                      ..
                rdfs:label              "installation" ;
                ..                      ..
        """
        installation = URIRef(base_str + "installation")
        
        g.add( (installation, RDF.type,            URIRef(waves.Installation)) )
        g.add( (installation, RDFS.label,          Literal("installation")) )
        g.add( (installation, waves.name,          Literal(self.projectInfo.name)) )
        g.add( (installation, waves.description,   Literal(self.projectInfo.description)) )
        g.add( (installation, waves.license,       Literal(self.projectInfo.license)) )
        g.add( (installation, waves.version,       Literal(self.projectInfo.version)) )
        g.add( (installation, waves.createdAt,     Literal(self.projectInfo.createdAt)) )
        
        # SETP 2: Parse cluster info
        """
            Output like :
                ..                      ..
                waves:zookeeperHosts    "localhost:port" ;
                waves:redisHost         "localhost:port" ;
                waves:mongoHost         "localhost:port" ;
                waves:influxHost        "localhost:port" ;
        """
        g.add( (installation, waves.redisHost,     Literal(self.clusterInfo.redisHost) ) )
        g.add( (installation, waves.mongoHost,     Literal(self.clusterInfo.mongoHost) ) )
        g.add( (installation, waves.influxHost,    Literal(self.clusterInfo.influxHost) ) )
        for zookeeperHost in self.clusterInfo.zookeeperHosts:
            g.add( (installation, waves.zookeeperHosts , Literal(zookeeperHost) ) )
        for kafkaHost in self.clusterInfo.kafkaHosts:
            g.add( (installation, waves.kafkaHosts , Literal(kafkaHost) ) )
        
        # STEP 3: Add Workflow Info
        """
            Output like :
                - N component each component like :
                <componentType/wavesId>
                    rdf:type                waves:componentType ;
                    waves:id                "wavesIdNumber"^^xsd:integer ;
                    waves:installation      <installation> ;
                    ..                      ..
                    waves:paramX            valuex.
                    
                or
                - N component with blank node like :
                <{filter|scouter}/wavesId>
                    rdf:type                waves:{Filter|Scouter} ;
                    waves:id 				"wavesIdNumber"^^xsd:integer ;
                    waves:installation      <installation> ;
                    ..                      ..
                    waves:consumesStreams   _:FId_SId ;
                    waves:staticFeed        _:bx ;
        """
        
        blank_node_types = ["RdfStore", "SparqlFeed", "RdfFeed", "RSSFeed", \
                            "FacebookFeed", "TwitterFeed", "OpenDataFeed"]
        duration_props   = ["stepRate", "duration", "frequency", "windowSpan", \
                            "refreshInterval", "eventRate", "allowedDuration", "initTime"]
        datetime_props   = ["startDate", "endDate"]
        time_props       = ["allowedDuration", "initTime"]
        integer_props    = ["numTasks", "workers", "id", "samplingParameter", \
                            "broadcastThreshold", "concurrentJobs", "numberRepartitions", "shuffledPartitions"]
        double_props     = []

        # Iterate to attach configuration parameters to component 
        # cmpt_nodes is for the following linkage usage
        cmpt_nodes = {}
        for cmpt in self.workflow.cmpt_list:
            
            lower_first = lambda s: s[:1].lower() + s[1:] if s else ''
            
            if cmpt.cmptType in blank_node_types:
                node = BNode()
            else:
                # For Filter, Strider and DRSS, they all have the same component type Filter
                if cmpt.cmptType in ['Filter', 'Strider', 'DRSS']:
                    name = 'filter'
                else:
                    # Lower case first letter
                    name = lower_first(cmpt.cmptType)
                if 'id' in cmpt.settings:
                    # Appendix ex. : <stream/1>
                    appendix = cmpt.settings['id']
                    node = URIRef(base_str + name + '/' + appendix)
                else:
                    node = URIRef(base_str + name)
                # Add installation
                g.add( (node, waves.installation , installation ) )
            
            cmpt_nodes[cmpt] = node
            
            # Add type for each component
            if cmpt.cmptType in ['Filter', 'Strider', 'DRSS']:
                # For Filter, Strider and DRSS, they all have the same component type Filter
                g.add((node, RDF.type, URIRef(waves_str + 'Filter')))
            else:
                g.add( (node, RDF.type , URIRef(waves_str + cmpt.cmptType ) ) )
            
            # Iterate each settings to add into configuration
            for key, value in cmpt.settings.items():
                if key == "label":
                    g.add( (node, RDFS.label, Literal(value) ) )
                elif key in duration_props:
                    g.add( (node, URIRef(waves_str + key ), Literal(value, datatype=XSD.duration) ) )
                elif key in datetime_props:
                    g.add( (node, URIRef(waves_str + key ), Literal(value, datatype=XSD.dateTime) ) )
                elif key in time_props:
                    g.add((node, URIRef(waves_str + key), Literal(value, datatype=XSD.time)))
                elif key in integer_props:
                    g.add( (node, URIRef(waves_str + key ), Literal(value, datatype=XSD.int) ) )
                elif key in double_props:
                    g.add( (node, URIRef(waves_str + key ), Literal(value, datatype=XSD.double) ) )
                elif key == "cmpt_type":
                    pass # do nothing
                elif key in ["locations", "pages", "hashTags"]:
                    for v in value.split(" || "):
                        g.add( (node, URIRef(waves_str + key ), Literal(v) ) )
                else:
                    g.add( (node, URIRef(waves_str + key ), Literal(value) ) )
        
        # print( self.workflow.link_list )        
        
        # Iterate links to add linkage information and linkage settings
        """
            Add properties for connection between components :
                - waves:consumesStreams   _:FId_SId
                -  [
                    - waves:someComponent      <SomeComponent/wavesId>
                    - rdfs:label		"FId_SId"
                    - waves:windowSpan	"PT900S"^^xsd:duration
                ]
        """
        for link in self.workflow.link_list:
            
            srcCmpt = link.srcCmpt
            trgCmpt = link.trgCmpt
            srcNode = cmpt_nodes[srcCmpt]
            trgNode = cmpt_nodes[trgCmpt]
            
            if srcCmpt.cmptType == 'Stream' and trgCmpt.cmptType in ["Filter", "Strider"]:
                
                # Use a blank node to save the connection and give window span settings
                bnode = BNode()
                # Add connections
                g.add( (bnode, waves.stream, srcNode ) )
                g.add( (trgNode, waves.consumesStream, bnode ) )
                
                # Add label, label equals {FILTER_ID}_{STREAM_ID} ex. : F-3_S-1
                b_label = ''
                if 'id' in trgCmpt.settings and 'id' in srcCmpt.settings:
                    b_label = 'F-' + trgCmpt.settings['id'] + '_' + 'S-' + srcCmpt.settings['id']
                g.add( (bnode, RDFS.label, Literal(b_label) ) )
                # Add settings
                for key, value in link.settings.items():
                    g.add( (bnode, URIRef(waves_str + key ), Literal(value) ) )
            
            if srcCmpt.cmptType in ['Stream'] :
                g.add( (trgNode, waves.consumesStreams, srcNode ) )
            elif srcCmpt.cmptType in ['RawStream'] :
                g.add( (trgNode, waves.consumesStream, srcNode ) )
            elif trgCmpt.cmptType in ['Stream', 'RawStream'] :
                g.add( (srcNode, waves.producesStream, trgNode ) )
            elif srcCmpt.cmptType == 'RdfStore' and trgCmpt.cmptType == "Filter":
                g.add( (trgNode, waves.rdfStore, srcNode ) )
            elif srcCmpt.cmptType == 'Sink' and trgCmpt.cmptType == "RdfStore":
                g.add((srcNode, waves.rdfStore, trgNode))
            elif srcCmpt.cmptType in ['SparqlFeed', 'RdfFeed'] and trgCmpt.cmptType == "Filter":
                g.add( (trgNode, waves.staticFeed, srcNode ) )
            elif trgCmpt.cmptType == "Scouter":
                g.add( (trgNode, waves.staticFeed, srcNode ) )
            elif srcCmpt.cmptType == 'AnomalyDetection' and trgCmpt.cmptType == "RdfStore":
                g.add((srcNode, waves.store, trgNode))
            else:
                # Temporal use linksTo predicate for connection of nodes
                g.add( (srcNode, waves.linksTo, trgNode ) )
        
        # SETP 4: Parse Metrics info
        metrics = BNode()
        g.add( (installation, waves.metrics , metrics) )
        g.add( (metrics, waves.frequency , Literal(self.metrics.frequency, datatype=XSD.duration) ) )
        g.add( (metrics, waves.reporters , Literal(self.metrics.reporters) ) )
        
        # SETP 5: Parse Clock info
        clock = BNode()
        g.add( (installation, waves.clock , clock) )
        g.add( (clock, waves.localTimeZone , Literal(self.clock.localTimeZone) ) )
        if self.clock.localTimeZone == "True":
            g.add( (clock, waves.startDate , Literal(self.clock.startDate, datatype=XSD.dateTime) ) )
            g.add( (clock, waves.endDate ,   Literal(self.clock.endDate, datatype=XSD.dateTime) ) )
            g.add( (clock, waves.duration ,  Literal(self.clock.duration, datatype=XSD.duration) ) )
        else:
            g.add( (clock, waves.startDate , Literal(self.clock.startDate, datatype=XSD.dateTime) ) )
            g.add( (clock, waves.acceleration , Literal( self.clock.acceleration, datatype=XSD.float) ) )
            
        serialize_result = g.serialize(format='trig', base=Namespace(base_str) ).decode('utf-8')
        
        # The rdflib api has a bug with base uri & graph uri
        # The generated string is like this:
        #
        # @prefix ns1: <http://www.waves-rsp.org/configuration#> .
        # ...
        # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        #
        # _:N1567dc0bb37d47e6926ac110de3235fa {
        #       <installation> a ns1:Installation ;
        # ...
        # }
        #
        # Need to do some small string replacement for add the base uri
        # I have tried many times but the base uri is always not working so have to do the replacement
        
        lines = serialize_result.split('\n')
        length = len(lines)
        
        for index, line in enumerate(lines):
            if index > 0 and index < length-1:
                # Judge by lines to see if the string need to be changed
                prev_line = lines[index-1]
                curr_line = lines[index]
                next_line = lines[index+1]
                
                # Conditions
                # 1: previous line has prefix value
                # 2: current line is empty
                # 3: Next line contains "{"
                if "prefix" in prev_line and not curr_line and "{" in next_line:
                    lines[index+1] = "<http://localhost:9091/waves/" + self.projectInfo.name + "> {"
                    lines.insert( index, "@base <http://localhost:9091/waves/versailles/> .")
        
        trig = '\n'.join(lines)

        # TODO: Replace '\r\n' with '\n' in TriG string

        return trig