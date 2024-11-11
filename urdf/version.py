from .onshape import Onshape

def get_document_versions(api: Onshape, document: str, type: str):
    path = f"/api/documents/d/{document}/{type}"
    res, success = api.send_request("get", path)

    if not success:
        return None
    
    return res.json()

class OnshapeVersion:
    def __init__(self, type: str, id: str):
        self.type = type
        self.id = id

    def get(self):
        return f"{self.type}/{self.id}"

    def normalize(self, api: Onshape, document: str):
        if self.type != "m":
            return self

        versions = get_document_versions(api, document, "versions")
        if versions is not None:
            for version in versions:
                if version["microversion"] == self.id:
                    return OnshapeVersion("v", version["id"])
        
        workspaces = get_document_versions(api, document, "workspaces")
        if workspaces is not None:
            for workspace in workspaces:
                if workspace["microversion"] == self.id:
                    return OnshapeVersion("w", version["id"])
        
        return self