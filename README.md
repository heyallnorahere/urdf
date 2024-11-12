# urdf

This script converts Onshape assemblies to ROS URDF files.

**This script may produce undefined behavior if the assembly has conflicts.**

CLI usage:
```bash
# enter repository root
cd .../src/urdf

# set your api keys!
export ONSHAPE_ACCESS_KEY= # your access key
export ONSHAPE_SECRET_KEY= # your secret key

# $URDF_DIRECTORY is the directory in which config.json and your output urdf file are placed
python -m urdf $URDF_DIRECTORY
```

Example `config.json`:
```json
{
    // these can be taken from the onshape url (e.g. https://cad.onshape.com/documents/{document id}/v/{version id}/...)
    "document": "...",
    "version": "...",
    "assembly": "Assembly 1",

    // model path prefix
    "stl_prefix": "my_package/resource",

    // robot name
    "name": "my_robot"
}
```