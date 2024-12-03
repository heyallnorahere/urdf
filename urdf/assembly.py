from .onshape import Onshape
from .version import OnshapeVersion
from .part_studio import Part

import numpy as np

def vector(value: list[float]):
    return np.array(value, dtype=np.float64, copy=True).reshape(len(value), 1)

class Occurrence:
    def __init__(self, path: list[str], transform: list[float], fixed: bool):
        self.path = path
        self.transform = np.array(transform, dtype=np.float64, copy=True).reshape(4, 4)
        self.fixed = fixed

class MatedOccurrence:
    def __init__(self, path: list[str], i: list[float], j: list[float], k: list[float], position: list[float]):
        self.path = path
        self.i = vector(i)
        self.j = vector(j)
        self.k = vector(k)
        self.position = vector(position)

class Mate:
    def __init__(self, data):
        self.type: str = data["mateType"]
        self.occurrences: list[MatedOccurrence] = []

        for entity in data["matedEntities"]:
            connector = entity["matedCS"]
            i = connector["xAxis"]
            j = connector["yAxis"]
            k = connector["zAxis"]
            position = connector["origin"]

            path = entity["matedOccurrence"]
            self.occurrences.append(MatedOccurrence(path, i, j, k, position))

class Group:
    def __init__(self, data):
        self.occurrences: list[list[str]] = []
        for occurrence in data["occurrences"]:
            self.occurrences.append(occurrence["occurrence"])

class Assembly:
    def __init__(self, api: Onshape, document: str, version: OnshapeVersion, id: str, name: str):
        self.api = api
        self.document = document
        self.version = version
        self.id = id
        self.name = name

        self.data = None
    
    def verify_loaded(self):
        if self.data is not None:
            return

        path = f"/api/assemblies/d/{self.document}/{self.version.get()}/e/{self.id}"
        query = {
            "includeMateFeatures": "true",
            "includeNonSolids": "true"
        }

        res, success = self.api.send_request("get", path, query)
        if not success:
            raise FileNotFoundError(f"Could not retrieve assembly: {self.id}")
        
        self.data = res.json()

    def get_instances(self):
        self.verify_loaded()

        instance_data = self.data["rootAssembly"]["instances"]
        instances: dict[str, Assembly | Part] = {}

        for data in instance_data:
            document_id = data["documentId"]
            element_id = data["elementId"]

            version = OnshapeVersion("m", data["documentMicroversion"])
            version = version.normalize(self.api, document_id)

            if data["type"] == "Assembly":
                instance = Assembly(self.api, document_id, version, element_id, "<implicit assembly>")
            elif data["type"] == "Part":
                instance = Part(self.api, document_id, version, element_id, data["partId"], "<implicit part>")
            else:
                continue

            instances[data["id"]] = instance

        return instances
    
    def get_features(self) -> dict[str, Mate | Group]:
        self.verify_loaded()

        features = {}
        feature_data = self.data["rootAssembly"]["features"]

        for feature in feature_data:
            id = feature["id"]
            type = feature["featureType"]
            data = feature["featureData"]

            if type == "mateGroup":
                final_feature = Group(data)
            elif type == "mate":
                final_feature = Mate(data)
            else:
                continue

            features[id] = final_feature
        
        return features
    
    def get_occurrences(self):
        self.verify_loaded()

        occurrence_data = self.data["rootAssembly"]["occurrences"]
        occurrences: list[Occurrence] = []

        for data in occurrence_data:
            occurrences.append(Occurrence(data["path"], data["transform"], data["fixed"]))
        
        return occurrences