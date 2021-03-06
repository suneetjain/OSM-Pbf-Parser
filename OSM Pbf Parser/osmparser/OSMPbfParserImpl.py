
from osmparser.IOSMPbfParser import IOSMPbfParser
from imposm.parser import OSMParser 
from PFinderConfig import dbNodesCollection, dbRelationsCollection
from PFinderConfig import dbWaysCollection
from PFinderConfig import dbCoordsCollection
from FetchWaysUtil import fetchNodesForWays2
from FetchWaysUtil import fetchPedestrian2
class OSMPbfParserImpl:
    def __init__(self,interface,osmPbfFile,callback_type=None,repository=None):
        if not isinstance(interface, IOSMPbfParser): raise Exception("Bad Interface")
        self.osmPbfFile = osmPbfFile
        if(callback_type== "nodes_callback"):
            self.parser = OSMParser(concurrency=4,nodes_callback=self.fetchNodes)
            print ("Initializing Nodes Callback......")
        elif(callback_type== "ways_callback"):
            self.parser = OSMParser(concurrency=4,ways_callback=self.fetchWays)
            print ("Initializing Ways Callback......")
        elif(callback_type== "relations_callback"):
            self.parser = OSMParser(concurrency=4,relations_callback=self.fetchRelations)
            print ("Initializing Relations Callback......")
        elif(callback_type== "coords_callback"):
            self.parser = OSMParser(concurrency=4,coords_callback=self.fetchCoords)
            print ("Initializing Coords Callback......")
        else:
            self.parser = OSMParser()
        self.repository= repository
    def start(self):
        print ("Started Parser.......")
        self.parser.parse(self.osmPbfFile)    
    def fetchNodes(self,nodes_tuple):
        waysCollection = self.repository.getCollection(dbWaysCollection)
        nodesCollection = self.repository.getCollection(dbNodesCollection)
        for osmId, meta_data,coords in nodes_tuple:

            value = fetchNodesForWays2(osmId, meta_data, coords, waysCollection)
            if value != None:
                try:
                    rec_id = nodesCollection.insert_one(value).inserted_id
                except Exception as e:
                    print (e)
                
                
    
    def fetchWays(self,ways_tuple,collection=None):
        collection=self.repository.getCollection(dbWaysCollection)
        for osmId, meta_data,refs in ways_tuple:
            value=fetchPedestrian2(osmId,meta_data,refs)
            if value != None and collection!=None:
                try:
                    rec_id=collection.insert_one(value).inserted_id
                except Exception as e:
                    print (e)
                
            
          
    def fetchRelations(self,relations_tuple):
        collection = self.repository.getCollection(dbRelationsCollection)
        for osmId, meta_data, refs in relations_tuple:
            try:
                if meta_data['type'] == 'route' and (meta_data['route'] == "bicycle" or meta_data['route'] == "mtb"):
                    relations_object = {}
                    relations_object['osmId'] = osmId
                    relations_object['metaData'] = meta_data
                    relations_object['refs'] = []
                    for ref in refs:
                        if ref[1] == "way":
                            relations_object['refs'].append(ref[0])
                    collection.insert_one(relations_object)
                else:
                    print ("skipping other route")
            except Exception as e:
                print (e)
        
    def fetchCoords(self,coords_tuple):
        collection = self.repository.getCollection(dbCoordsCollection)
        for osmId,lat,lng in coords_tuple:
            coordsObj = {}
            coordsObj['osmId'] = osmId
            coordsObj['lat']= lat
            coordsObj['lng']= lng
            collection.insert_one(coordsObj)
