import os, re

class TransientCWD:
    import os

    def __init__(self, new_cwd):
        self.new_cwd = os.path.abspath(os.path.dirname(new_cwd))

    def __enter__(self):
        # On start of indented block, save current working dir
        self.prev_cwd = os.getcwd()

        # Change the working dir to the new one
        os.chdir(self.new_cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # On end of indented block, revert back to prev working dir
        os.chdir(self.prev_cwd)

class MorphologyPoint:
    next_point_id = 1

    def __init__(self, prox_dist_tag, nml_segment):
        self.x = float(prox_dist_tag.attrib['x'])
        self.y = float(prox_dist_tag.attrib['y'])
        self.z = float(prox_dist_tag.attrib['z'])
        self.diam = float(prox_dist_tag.attrib['diameter'])
        self.radius = self.diam / 2.0


        self.nml_segment = nml_segment

        self.parent = None
        self.id = self.get_next_id()
        self.type = swc_type_from_section_name(nml_segment.name)

        self.added = False

    def get_next_id(self):
        result = MorphologyPoint.next_point_id
        MorphologyPoint.next_point_id += 1
        return result

    def same_as(self, other):
        return (self.x == other.x and
                self.y == other.y and
                self.z == other.z and
                self.diam == other.diam)

    def __str__(self):
        return str({'x':self.x,'y':self.y,'z':self.z,'d':self.diam,'id':self.id,'type':self.type,'added':self.added})

class NmlSegment:
    all_segments = {}

    def __init__(self, segment_tag, schema):
        self.name = segment_tag.attrib.get('name')
        self.id = int(segment_tag.attrib.get('id'))
        self.parent_id = int(segment_tag.attrib.get('parent')) if 'parent' in segment_tag.attrib else None

        self.children = []
        self.parent = self.link_parent()
        self.all_segments[self.id] = self

        prox, dist = segment_tag.findall(schema+'proximal'), segment_tag.findall(schema+'distal')

        # Could have just proximal, no parent
        # proximal and parent, both identical
        # proximal and parent, both different
        # just parent

        # No parent
        if self.parent_id is None:
            # Has proximal
            if prox:
                self.proximal = MorphologyPoint(prox[0], nml_segment=self)
            else:
                raise Exception("In the NeuroML file, segment "+ str(self.id) +" has neither a parent nor a proximal element.")

        # Has a parent
        else:
            # Just parent, no proximal
            if not prox:
                self.proximal = self.parent.distal

            # Parent and proximal
            else:
                my_proximal = MorphologyPoint(prox[0], nml_segment=self)

                # prox and parent distal are identical
                if self.parent.distal.same_as(my_proximal):
                    self.proximal = self.parent.distal

                # not identical
                else:
                    self.proximal = my_proximal

        self.distal = MorphologyPoint(dist[0], nml_segment=self)

    def link_parent(self):
        if self.parent_id is not None:
            if self.parent_id not in self.all_segments:
                raise Exception("In the NeuroML file, a segment "+ self.id +" refers to a non-existent parent segment: " + self.parent_id)
            else:
                parent = self.all_segments[self.parent_id]

                if parent.id == self.id:
                    raise Exception("In the NeuroML file, a segment " + self.id + " is its own parent.")

                parent.children.append(self)

                return parent

        else:
            return None

    def get_child_SWC_points(self, swc_points = None):
        if not swc_points:
            swc_points = []

        # Collect the points
        self.add_point_to_SWC(self.proximal, swc_points)
        self.add_point_to_SWC(self.distal, swc_points)

        # Set the proximal point's parent point, if not set already and segment has a parent
        if not self.proximal.parent and self.parent:
            self.proximal.parent = self.parent.distal

        self.distal.parent = self.proximal

        for child_node in self.children:
            child_node.get_child_SWC_points(swc_points)

        return swc_points

    def add_point_to_SWC(self, point, collection):
        if not point.added:
            collection.append(point)
            point.added = True

    def __str__(self):
        return str({'id':self.id,'name':self.name,'parent':self.parent})

def get_cell_template_names(hoc_path):
    '''
    Get the hoc cell template name

    :param hoc_path:
    :return:
    '''

    with open(hoc_path, 'r') as f:
        hoc_content = f.read()

    hoc_template_name_matches = re \
        .compile('begintemplate (.*)') \
        .findall(hoc_content)

    if len(hoc_template_name_matches) > 0:
        return hoc_template_name_matches
    else:
        return None

def neuron2neuroml(nml_path):
    '''
    Saves any instantiated cells in NEURON and saves their morpholoogy as NeuroML

    :param nml_path: The path to NeuroML file
    '''
    from neuron import h
    h.define_shape()  # Handle models without h.xyz3d() data
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

    # Load the hoc file
    from neuron import h, gui
    h.load_file(hoc_path)

    # Check if the hoc file defines any templates
    cell_names = get_cell_template_names(hoc_path)

    if cell_names is not None:
        cells = []

        # Instantiate each defined template
        for name in cell_names:
            cells.append(getattr(h, name)())

    # Convert the instantiated cell files to NeuroML and then to SWC
    neuron2swc(swc_path)


def neuron2swc(swc_path, cleanup=True):
    # Convert NEURON instantiated cell morphology to NeuroML
    swc_dir = os.path.dirname(swc_path)
    nml_path = os.path.join(swc_dir, os.path.basename(swc_path) + ".nml")
    neuron2neuroml(nml_path)

    # Then convert the NeuroML file to swc
    neuroml2swc(nml_path, swc_path)

    # Cleanup - remove NeuroML file
    if cleanup:
        os.remove(nml_path)


def swc_type_from_section_name(section_name):
    '''
    Returns an integer string of an SWC point type in response to a string name of a NEURON section.

    See column 2 of http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html

    To map custom section names to parts of SWC cell, override this method. E.g:

    # Create a new name->type map
    def new_map(section_name):
        return "5" if "blah" in section_name else "1"

    # Replace the default map with the new one. Subsequent hoc2swc statements will use the new map.
    from hoc2swc import swc_type_from_section_name
    swc_type_from_section_name.__code__ = new_map.__code__

    :param section_name: name string of a NEURON section
    :return: integer string e.g. "1" or "3" that corresponds to a SWC point type
    '''

    if "den" in section_name:
        if "apical" in section_name:
            return "4"

        return "3"

    if "axon" in section_name or "hillock" in section_name or "initial" in section_name:
        return "2"

    if "soma" in section_name:
        return "1"

    return "5"


def neuroml2swc(nml_path, swc_path, swap_yz=True):
    import xml.etree.ElementTree, re

    root = xml.etree.ElementTree.parse(nml_path).getroot()
    cells = [e for e in root.findall(".//") if e.tag.endswith('cell')]

    for c, cell in enumerate(cells):
        # Extract the segment XML schema from the first cell segment tag
        try:
            first_seg = next(e for e in cell.findall(".//") if e.tag.endswith('segment'))
        except:
            raise Exception("Did not find any segments for the cell. This can sometimes happen if h.define_shape() was not executed first.")

        seg_schema = re.compile('(\{.*\})').findall(first_seg.tag)[0]

        # Get the list of all cell segments
        seg_tags = cell.findall(".//"+seg_schema+"segment")

        root_segment = None
        MorphologyPoint.next_point_id = 1

        # Parse the segments into a tree structure, keeping the root
        for s, seg_tag in enumerate(seg_tags):
            parsed_segment = NmlSegment(seg_tag, seg_schema)

            if s == 0:
                root_segment = parsed_segment


        # Traverse the tree, depth-first to generate the list of SWC points
        swc_points = root_segment.get_child_SWC_points()

        if len(cells) == 1:
            file_path = swc_path

        else:
            dir = os.path.dirname(swc_path)
            file_stem, file_ext = os.path.splitext(os.path.basename(swc_path))
            index = str(c).zfill(4)

            file_path = os.path.join(dir, file_stem + "_" + index + file_ext)

        with open(file_path, "w") as file:
            for point in swc_points:
                file.write(
                    str(point.id) + " " +
                    point.type + " " +
                    str(point.x) + " " +
                    (str(point.z) if swap_yz else str(point.y)) + " " +
                    (str(point.y) if swap_yz else str(point.z)) + " " +
                    str(point.radius) + " " +
                    str(point.parent.id if point.parent else -1) + "\n")

        print("Wrote cell "+str(c)+" to " + file_path)

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
            raise Exception("NEURON process crashed. See above for error details.")

    else:
        hoc2neuroml(hoc_path, mod_path, swc_path)




