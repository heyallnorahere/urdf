from .onshape import Onshape
from .version import OnshapeVersion
from .part_studio import Part

class Occurrence:
    def __init__(self, path: list, transform: list):
        self.path = path
        self.transform = transform

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
    
    def get_features(self) -> list:
        self.verify_loaded()
        return self.data["rootAssembly"]["features"]
    
    def get_occurrences(self):
        self.verify_loaded()

        occurrence_data = self.data["rootAssembly"]["occurrences"]
        occurrences: list[Occurrence] = []

        for data in occurrence_data:
            occurrences.append(Occurrence(data["path"], data["transform"]))
        
        return occurrences