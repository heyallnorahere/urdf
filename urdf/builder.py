from .assembly import Assembly
from .part_studio import Part

from urdfpy import URDF, Link, Joint, Visual, Collision, Inertial
from os import makedirs
from os.path import join, dirname

def part_identifier(part: Part):
    document = part.document
    version = part.version.get()
    studio = part.studio
    id = part.id

    return f"{document}/{version}/{studio}/{id}"

def assembly_identifier(assembly: Assembly):
    document = assembly.document
    version = assembly.version.get()
    id = assembly.id

    return f"{document}/{version}/{id}"

class Builder:
    def __init__(self, stl_prefix: str):
        self.stl_prefix = stl_prefix
    
    def build(self, workdir: str, assembly: Assembly, robot_name: str):
        occurrences = assembly.get_occurrences()
        exported_stls = []
        instance_lists: dict[str, dict[str, Assembly | Part]] = {}

        links = []
        joints = []

        for occurrence in occurrences:

            current_node = assembly
            for id in occurrence.path:
                if not isinstance(current_node, Assembly):
                    break

                identifier = assembly_identifier(current_node)
                if identifier not in instance_lists:
                    print(f"Found new assembly: {identifier}")
                    instance_lists[identifier] = current_node.get_instances()

                instances = instance_lists[identifier]
                current_node = instances[id]
            
            if not isinstance(current_node, Part):
                continue
            
            identifier = part_identifier(current_node)
            if not identifier in exported_stls:
                exported_stls.append(identifier)

                stl_path = f"{workdir}/{identifier}.stl"
                makedirs(dirname(stl_path), exist_ok=True)

                stl_output = open(stl_path, "wb")
                current_node.export_stl(stl_output)
                stl_output.close()

            link_name = "/".join(occurrence.path)
            #links.append(Link(link_name))
        
        output_path = join(workdir, f"{robot_name}.urdf")
        output = open(output_path, "w")

        desc = URDF(robot_name, links, joints)
        #desc.save(output)

        output.close()