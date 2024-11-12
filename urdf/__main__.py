from sys import argv
from os import getenv, getcwd
from os.path import join, exists, abspath
import json

from .onshape import Onshape, OnshapeAuth
from .document import Document
from .assembly import Assembly
from .builder import Builder
from .version import OnshapeVersion

def get_config(config, key: str, default=None):
    if key in config:
        return config[key]
    
    if default is None:
        raise KeyError(f"Required config value not present: {key}")
    
    return default

workdir = getcwd()
if len(argv) > 1:
    workdir = abspath(argv[1])
    if not exists(workdir):
        raise FileNotFoundError(f"No such directory: {workdir}")
    
config_path = join(workdir, "config.json")
config_file = open(config_path, "r")
config = json.load(config_file)
config_file.close()

access_key = getenv("ONSHAPE_ACCESS_KEY")
auth = None

if access_key is not None:
    secret_key = getenv("ONSHAPE_SECRET_KEY")
    auth = OnshapeAuth(access_key, secret_key)

document_id = get_config(config, "document")
document_version = OnshapeVersion("v", get_config(config, "version"))

print(f"Connecting to Onshape {'not using' if auth is None else 'using'} auth keys")
onshape = Onshape(auth)

print(f"Loading document {document_id} on version {document_version.id}")
document = Document(onshape, document_id, document_version)

elements = document.get_elements()
if elements is None:
    raise RuntimeError("Failed to retrieve elements for document")

assembly = None
assemblyName = get_config(config, "assembly")
for element in elements:
    if isinstance(element, Assembly) and element.name == assemblyName:
        assembly = element

if assembly is None:
    raise FileNotFoundError(f"Failed to find assembly: {assemblyName}")

print(f"Found assembly of name {assemblyName}")
builder = Builder(get_config(config, "stl_prefix", ""))
builder.build(workdir, assembly, get_config(config, "name", assemblyName))