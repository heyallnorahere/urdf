from io import BufferedWriter

from .onshape import Onshape
from .version import OnshapeVersion

class Part:
    def __init__(self, api: Onshape, document: str, version: OnshapeVersion, studio: str, id: str, name: str):
        self.api = api
        self.document = document
        self.version = version
        self.studio = studio
        self.id = id
        self.name = name
    
    def export_stl(self, file: BufferedWriter) -> bool:
        url = f"/api/parts/d/{self.document}/{self.version.get()}/e/{self.studio}/partid/{self.id}/stl"
        query = {
            "units": "millimeter"
        }

        res, success = self.api.send_request("get", url, query)
        if not success:
            return False
        
        file.write(res.content)
        file.flush()

        return True
    
    def get_physical_properties(self):
        url = f"/api/partstudios/d/{self.document}/{self.version.get()}/e/{self.studio}/massproperties"
        query = {
            "partId": self.id
        }

        res, success = self.api.send_request("get", url, query)
        if not success:
            return None
        
        data = res.json()
        return data["bodies"][self.id]

class PartStudio:
    def __init__(self, api: Onshape, document: str, version: OnshapeVersion, id: str, name: str):
        self.api = api
        self.document = document
        self.version = version
        self.id = id
        self.name = name
    
    def get_parts(self):
        url = f"/api/parts/d/{self.document}/{self.version.get()}/e/{self.id}"
        res, success = self.api.send_request("get", url)

        if not success:
            return None
        
        data = res.json()
        parts: list[Part] = []

        for part_data in data:
            name = part_data["name"]
            id = part_data["id"]

            parts.append(Part(self.api, self.document, self.version, self.id, id, name))
        
        return parts