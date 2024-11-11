# urdf

This script converts Onshape assemblies to ROS URDF files.

Must be run on Python<3.7 due to errors in the URDF library lol

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

    // model prefix (e.g. my_package/resource)
    "stl_prefix": ".../...",

    // robot name
    "name": "my_robot"
}
```