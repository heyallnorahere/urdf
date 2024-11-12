from .assembly import Assembly, Occurrence, Mate, Group
from .part_studio import Part

from os import makedirs
from os.path import join, dirname
from lxml.etree import Element, _Element, tostring

import numpy as np
import numpy.linalg as linalg
import base64
from typing import Any

def part_identifier(part: Part) -> str:
    document = part.document
    version = part.version.get()
    studio = part.studio

    # encoding to avoid slashes in the name
    id = base64.b64encode(part.id.encode()).decode()

    return f"{document}/{version}/{studio}/{id}"


def assembly_identifier(assembly: Assembly) -> str:
    document = assembly.document
    version = assembly.version.get()
    id = assembly.id

    return f"{document}/{version}/{id}"


# https://github.com/mmatl/urdfpy/blob/master/urdfpy/utils.py
def matrix_to_rpy(matrix, alt=False):
    R = np.asanyarray(matrix, dtype=np.float64)
    r = 0
    p = 0
    y = 0

    if np.abs(R[2, 0]) >= 1.0 - 1e-12:
        y = 0
        p = np.pi / 2
        r = np.arctan2(R[0, 1], R[0, 2])

        if R[2, 0] > 0:
            p *= -1.0
    else:
        p = -np.arcsin(R[2, 0])
        if alt:
            p = np.pi - p

        r = np.arctan2(R[2, 1], R[2, 2])
        y = np.arctan2(R[1, 0], R[0, 0])

    return np.array([r, p, y], dtype=np.float64)

class Link:
    def __init__(self, mesh: str, occurrence: Occurrence):
        self.mesh = mesh
        self.occurrence = occurrence

class Builder:
    def __init__(self, stl_prefix=""):
        self.stl_prefix = f"package://{stl_prefix}/" if len(stl_prefix) > 0 else ""
        self.instance_lists: dict[str, dict[str, Assembly | Part]] = {}

    def get_instances(self, assembly: Assembly):
        identifier = assembly_identifier(assembly)
        if identifier not in self.instance_lists:
            print(f"Found new assembly: {identifier}")
            self.instance_lists[identifier] = assembly.get_instances()

        return self.instance_lists[identifier]

    def find_instance(self, path: list[str], root: Assembly) -> Assembly | Part:
        current_node = root
        for id in path:
            if not isinstance(current_node, Assembly):
                break

            instances = self.get_instances(current_node)
            current_node = instances[id]

    def build(self, workdir: str, assembly: Assembly, robot_name: str):
        occurrences = assembly.get_occurrences()
        exported_stls = []
        mates: dict[str, tuple[Occurrence, Mate]] = {}
        groups: dict[str, tuple[Occurrence, Group]] = {}
        links: dict[str, Link] = {}

        urdf: _Element = Element("robot", {"name": robot_name})
        for occurrence in occurrences:
            node = self.find_instance(occurrence.path, assembly)
            if isinstance(node, Assembly):
                features = node.get_features()
                for id in features:
                    path = occurrence.path.copy()
                    path.append(id)
                    feature_id = "/".join(path)

                    feature = features[id]
                    if isinstance(feature, Group):
                        groups[feature_id] = (occurrence, feature)
                    
                    if isinstance(feature, Mate):
                        mates[feature_id] = (occurrence, feature)

            if isinstance(node, Part):
                identifier = part_identifier(node)
                stl_stub = f"{identifier}.stl"

                if not identifier in exported_stls:
                    exported_stls.append(identifier)

                    stl_path = f"{workdir}/{stl_stub}"
                    makedirs(dirname(stl_path), exist_ok=True)

                    stl_output = open(stl_path, "wb")
                    node.export_stl(stl_output)
                    stl_output.close()
                
                link = Link(self.stl_prefix + stl_stub, occurrence)
                name = "/".join(occurrence.path)
                links[name] = link
        
        # todo: mate shit. i hate this
        # roll pitch and yaw

        print("Processing finished, writing URDF...")
        output_path = join(workdir, f"{robot_name}.urdf")
        output = open(output_path, "w")

        text = tostring(urdf, pretty_print=True, encoding="unicode")
        output.write(text)

        output.close()
        self.instance_lists = {}
