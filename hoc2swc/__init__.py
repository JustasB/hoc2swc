import os, re

class TransientCWD:
    import os

    def __init__(self, new_cwd):
        self.new_cwd = os.path.dirname(new_cwd)

    def __enter__(self):
        # On start of indented block, save current working dir
        self.prev_cwd = os.getcwd()

        # Change the working dir to the new one
        os.chdir(self.new_cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # On end of indented block, revert back to prev working dir
        os.chdir(self.prev_cwd)

def get_cell_template_name(hoc_path):
    '''
    Get the hoc cell template name

    :param hoc_path:
    :return:
    '''

    with open(hoc_path, 'r') as f:
        hoc_content = f.read()

    hoc_template_name = re \
        .compile('begintemplate (.*)') \
        .findall(hoc_content)[0]

    return hoc_template_name

def neuron2neuroml(nml_path):
    '''
    Saves any instantiated cells in NEURON and saves their morpholoogy as NeuroML

    :param nml_path: The path to NeuroML file
    '''
    from neuron import h
    h.load_file('mview.hoc')
    modelView = h.ModelView(0)
    modelXml = h.ModelViewXML(modelView)
    modelXml.xportLevel1(nml_path)

def compile_mod():
    import platform

    if platform.system() == "Windows":
        print("Make sure the .MOD files required by the .HOC file have been compiled before running this script. See: https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html")

    else:
        os.system("nrnivmodl")


def load_mod():
    import fnmatch, os, platform
    from neuron import h

    # Mod files might have already been loaded, loading them again crashes NEURON
    # Need to test if they've been loaded already
    # I cannot find a NEURON function that lists loaded mechanisms, but...
    # Trying to access them directly in Python results in an error - if the mechanism has been loaded
    # The strategy here is to check if tryting to access those mod files throws that error
    mod_files = [file.replace('.mod','') for file in os.listdir('.') if file.endswith('.mod')]

    mod_loaded = False
    for mod in mod_files:
        try:
            getattr(h, mod) # Results in TypeError if mod file has been loaded, else AttributeError
        except AttributeError:
            pass
        except TypeError:
            mod_loaded = True
            break

    # If none of the mod files have been loaded, load them
    if not mod_loaded:

        # First figure out where the compiled mod binaries are (platform dependent)
        dll_path = None
        target = "nrnmech.dll" if platform.system() == "Windows" else "libnrnmech.so"

        try:
            for root, dirnames, filenames in os.walk('.'):
                for filename in fnmatch.filter(filenames, target):
                    dll_path = os.path.join(root, filename)
                    raise StopIteration() # Stop looking once found

        except StopIteration:
            pass

        if dll_path is None:
            raise Exception("Could not find compiled NEURON .mod files. Their compilation failed or they "
                            "are located somewhere else. Looked for "+target+" here (inc. sub-dirs): " + os.getcwd())

        # Load the mod files from the binary
        from neuron import h
        h.nrn_load_dll(dll_path)


def hoc2neuroml(hoc_path, mod_path, swc_path):
    if not os.path.exists(hoc_path):
        raise OSError("No such file or directory: " + hoc_path)

    if not os.path.exists(mod_path):
        raise OSError("No such file or directory: " + mod_path)

    # Change to the dir where mod files are (to let NEURON auto-load the mod files)
    with TransientCWD(mod_path):
        compile_mod()
        load_mod()

    # Load the hoc file and instantiate the cell defined within
    from neuron import h
    h.load_file(hoc_path)
    cell_name = get_cell_template_name(hoc_path)
    cell = getattr(h, cell_name)()

    # Convert the instantiated cell files to NeuroML and then to SWC
    neuron2swc(swc_path)


def neuron2swc(swc_path):
    # Convert NEURON instantiated cell morphology to NeuroML
    swc_dir = os.path.dirname(swc_path)
    nml_path = os.path.join(swc_dir, os.path.basename(swc_path) + ".nml")
    neuron2neuroml(nml_path)

    # Then convert the NeuroML file to swc
    neuroml2swc(nml_path, swc_path)

    # Cleanup - remove NeuroML file
    os.remove(nml_path)


def neuroml2swc(nml_path, swc_path, swap_yz=True):
    import xml.etree.ElementTree, re
    from collections import OrderedDict

    root = xml.etree.ElementTree.parse(nml_path).getroot()

    # Extract the XML schema from the first segment tag
    first_seg = next(e for e in root.findall(".//") if e.tag.endswith('segment'))
    schema = re.compile('(\{.*\})').findall(first_seg.tag)[0]

    # Get the list of all cell segments
    seg_tags = root.findall(".//"+schema+"segment")

    # Treat each XYZ+D ending of a segment as separate "points"
    neuroml_point_ids = {}
    current_swc_id = 1

    for seg_tag in seg_tags:
        proximal = seg_tag.findall(schema+'proximal')
        distal   = seg_tag.findall(schema+'distal')

        for ending in [proximal, distal]:
            if len(ending) > 0:
                point_key = str(ending[0].attrib) # Ending's XYZ+D is its key

                if point_key not in neuroml_point_ids:
                    neuroml_point_ids[point_key] = str(current_swc_id)
                    current_swc_id += 1

    # Store the swc ids of each distal ending
    segment_distal_point_swc_ids = {}

    for seg_tag in seg_tags:
        distal = seg_tag.findall(schema+'distal')
        segment_distal_point_swc_ids[seg_tag.attrib["id"]] = neuroml_point_ids[str(distal[0].attrib)]

    swc_points = OrderedDict()

    def get_type(seg_tag):
        # Determine the SWC type of the segment.
        # See column 2 of http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html

        seg_name = seg_tag.attrib["name"].lower()

        if "dend" in seg_name:
            if "apical" in seg_name:
                return "4"

            return "3"

        if "axon" in seg_name:
            return "2"

        if "soma" in seg_name:
            return "1"

        return "5"

    for tag in seg_tags:
        parent_nml_id = tag.attrib.get('parent')
        proximal = tag.findall(schema+'proximal')
        distal   = tag.findall(schema+'distal')

        # Segment has parent?
        if parent_nml_id:

            # Has parent and proximal ending? Use proximal ending as point's parent
            if proximal:
                parent_id = neuroml_point_ids[str(proximal[0].attrib)]

                # If diameter of proximal is not the same as parent's distal - create proximal as separate point
                if parent_id not in swc_points:
                    if parent_nml_id not in segment_distal_point_swc_ids:
                        raise Exception("In the NeuroML file, a segment refers to non-existent parent segment: " + parent_nml_id)

                    swc_point = {
                        "id": parent_id,
                        "type": get_type(tag),
                        "parent": segment_distal_point_swc_ids[parent_nml_id],
                        "x": proximal[0].attrib["x"],
                        "y": proximal[0].attrib["y"],
                        "z": proximal[0].attrib["z"],
                        "radius": str(float(proximal[0].attrib["diameter"]) / 2.0)
                    }

                    swc_points[swc_point['id']] = swc_point

            # parent - no prox - use parent's distal as parent id
            else:
                parent_id = segment_distal_point_swc_ids[parent_nml_id]

        # no parent - add proximal, which will become distal's parent
        else:
            swc_point = {
                "id": neuroml_point_ids[str(proximal[0].attrib)],
                "type": get_type(tag),
                "parent": "-1",
                "x": proximal[0].attrib["x"],
                "y": proximal[0].attrib["y"],
                "z": proximal[0].attrib["z"],
                "radius": str(float(proximal[0].attrib["diameter"]) / 2.0)
            }

            parent_id = swc_point["id"]

            swc_points[swc_point['id']] = swc_point


        # Always add distal
        swc_point = {
            "id": neuroml_point_ids[str(distal[0].attrib)],
            "type": get_type(tag),
            "parent": str(parent_id),
            "x": distal[0].attrib["x"],
            "y": distal[0].attrib["y"],
            "z": distal[0].attrib["z"],
            "radius": str(float(distal[0].attrib["diameter"]) / 2.0)
        }

        swc_points[swc_point['id']] = swc_point

    with open(swc_path, "w") as file:
        for point in swc_points.values():
            file.write(
                point["id"] + " " +
                point["type"] + " " +
                point["x"] + " " +
                (point["z"] if swap_yz else point["y"]) + " " +
                (point["y"] if swap_yz else point["z"]) + " " +
                point["radius"] + " " +
                point["parent"] + "\n")

def hoc2swc(hoc_path, swc_path, mod_path=None, separate_process=True):

    # If not spec'd, assume mod files are in the hoc path
    if mod_path is None:
        mod_path = hoc_path

    # Once NEURON loads a hoc or mod file, it cannot be unloaded. Whole NEURON process has to be terminated to
    # ensure proper cleanup. This is especially important when converting multiple files in a single Python session.
    # By running NEURON in a separate process, we ensure past HOC/MOD files will not affect later HOC files.
    if separate_process:
        from multiprocessing import Process
        proc = Process(target=hoc2neuroml, args=(hoc_path, mod_path, swc_path,))
        proc.start()
        proc.join()
        print('exit code', proc.exitcode)
        if proc.exitcode > 0:
            raise Exception("Process crashed.")

    else:
        hoc2neuroml(hoc_path, mod_path, swc_path)

    print('Converted to SWC: ' + os.path.abspath(swc_path))
