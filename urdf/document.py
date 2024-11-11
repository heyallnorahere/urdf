from .onshape import Onshape
from .assembly import Assembly
from .part_studio import PartStudio
from .version import OnshapeVersion

class Document:
    def __init__(self, api: Onshape, id: str, version: OnshapeVersion):
        self.api = api
        self.id = id
        self.version = version

        self.data = self.get()
        if self.data is None:
            raise FileNotFoundError(f"Document {id} at version {version} does not exist!")
    
    def get(self):
        response, success = self.api.send_request("get", "/api/documents/" + self.id)
        if not success:
            return None
        
        return response.json()
    
    def get_elements(self):
        path = f"/api/documents/d/{self.id}/{self.version.get()}/elements"
        res, success = self.api.send_request("get", path)

        if not success:
            return None

        data = res.json()
        elements: list[Assembly | PartStudio] = []
        
        for element in data:
            if element["type"] == "Assembly":
                final_element = Assembly(self.api, self.id, self.version, element["id"], element["name"])
            elif element["type"] == "PartStudio":
                final_element = PartStudio(self.api, self.id, self.version, element["id"], element["name"])
            else:
                continue
            
            elements.append(final_element)
        
        return elements