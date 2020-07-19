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

    def __init__(self, i, h_section, h):
        self.x = round(h.x3d(i, sec=h_section), 3)
        self.y = round(h.y3d(i, sec=h_section), 3)
        self.z = round(h.z3d(i, sec=h_section), 3)
        self.diam = round(h.diam3d(i, sec=h_section), 3)
        self.radius = self.diam / 2.0
        self.loc_along = h.arc3d(i, sec=h_section) / h_section.L

        self.parent = None
        self.id = self.get_next_id()
        self.type = swc_type_from_section_name(h_section.name())

        self.added = False

    def get_next_id(self):
        result = MorphologyPoint.next_point_id
        MorphologyPoint.next_point_id += 1
        return result

class NeuronSection:

    def __init__(self, h_section, h, parent_NeuronSection = None):
        self.name = h_section.name()
        self.nseg = h_section.nseg

        self.points = [MorphologyPoint(i, h_section, h) for i in range(int(h.n3d(sec=h_section)))]
        self.children = [NeuronSection(sec, h, self) for sec in h_section.children()]

        self.distal = self.points[-1]
        self.proximal = self.points[0]

        if parent_NeuronSection:
            self.parent = parent_NeuronSection
            self.loc_along_parent = h_section.parentseg().x
        else:
            self.parent = None
            self.loc_along_parent = None

        self.orientation = int(h_section.orientation())

    def get_child_SWC_points(self, swc_points = None):
        if not swc_points:
            swc_points = []

        # Add section 3D points - and set their parents
        for i, point in enumerate(self.points):
            self.add_point_to_SWC(point, swc_points)

            # When orientation==0, the previous point is the parent of each non-proximal point
            if self.orientation == 0 and point != self.proximal:
                point.parent = self.points[i-1]

            # When orientation==1, the next point is the parent of each non-distal point
            else:
                if self.orientation == 1 and point != self.distal:
                    point.parent = self.points[i+1]

        # Set the parent point on another segment, based on orientation
        if self.parent:
            if self.orientation == 0 and not self.proximal.parent:
                self.proximal.parent = self.parent_point()

            else:
                if self.orientation == 1 and not self.distal.parent:
                    self.distal.parent = self.parent_point()

        for child_node in self.children:
            child_node.get_child_SWC_points(swc_points)

        return swc_points

    def parent_point(self):
        return self.parent.point_closest_to(self.loc_along_parent)

    def point_closest_to(self, loc):
        min_i = None
        min_dist = None

        # Try to short circuit the common locations
        if loc == 1.0:
            min_i = -1

        elif loc == 0.0:
            min_i = 0

        # Otherwise, find the 3d point with the nearest arc fraction to the desired fraction
        else:
            for i, point in enumerate(self.points):
                dist = abs(point.loc_along - loc)

                if min_i is None or min_dist > dist:
                    min_i = i
                    min_dist = dist

        return self.points[min_i]


    def add_point_to_SWC(self, point, collection):
        if not point.added:
            collection.append(point)
            point.added = True


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
            print("Warning: Could not find compiled NEURON .mod files. Their compilation failed or they "
                            "are located somewhere else. Looked for "+target+" here (inc. sub-dirs): " + os.getcwd())

        else:
            # Load the mod files from the binary
            from neuron import h
            h.nrn_load_dll(dll_path)


def _hoc2swc(hoc_path, mod_path, swc_path, no_mod):
    if not os.path.exists(hoc_path):
        raise OSError("No such file or directory: " + hoc_path)

    if not os.path.exists(mod_path):
        raise OSError("No such file or directory: " + mod_path)

    # If model does not have custom mod files (don't try to compile/load them)
    if not no_mod:
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
            cells.append(getattr(h, name.replace('\r',''))())

    # Convert the instantiated cell files to SWC
    neuron2swc(swc_path)


def neuron2swc(swc_path, swap_yz=False):
    from neuron import h

    h.define_shape()

    # Get cells -- root Sections
    cells = h.SectionList()
    cells.allroots()
    cells = [sec for sec in cells]

    for c, cell in enumerate(cells):

        # Reset the SWC point id for each cell
        MorphologyPoint.next_point_id = 1

        # Parse the Section tree, starting at the root
        root = NeuronSection(cell, h)

        # Traverse the tree, depth-first to generate the list of SWC points
        swc_points = root.get_child_SWC_points()

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


def swc_type_from_section_name(section_name):
    '''
    Returns an integer string of an SWC point type in response to a string name of a NEURON section.

    See column 2 of http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html

    To map custom section names to parts of SWC cell, override this method. E.g:

    # Create a new name->type map
    def new_map(section_name):
        return "5" if "foo" in section_name else "1"

    # Replace the default map with the new one. Subsequent hoc2swc statements will use the new map.
    from hoc2swc import swc_type_from_section_name
    swc_type_from_section_name.__code__ = new_map.__code__

    :param section_name: name string of a NEURON section
    :return: integer string e.g. "1" or "3" that corresponds to a SWC point type
    '''

    if "apic" in section_name:
        return "4"

    if "den" in section_name:
        return "3"

    if "axon" in section_name or "hillock" in section_name or "initial" in section_name:
        return "2"

    if "soma" in section_name:
        return "1"

    return "5"


def hoc2swc(hoc_path, swc_path, mod_path=None, separate_process=True, no_mod=False):

    # If not spec'd, assume mod files are in the hoc path
    if mod_path is None:
        mod_path = hoc_path

    # Once NEURON loads a hoc or mod file, it cannot be unloaded. Whole NEURON process has to be terminated to
    # ensure proper cleanup. This is especially important when converting multiple files in a single Python session.
    # By running NEURON in a separate process, we ensure past HOC/MOD files will not affect later HOC files.
    if separate_process:
        from multiprocessing import Process
        proc = Process(target=_hoc2swc, args=(hoc_path, mod_path, swc_path, no_mod,))
        proc.start()
        proc.join()
        print('exit code', proc.exitcode)
        if proc.exitcode > 0:
            raise Exception("NEURON process crashed. See above for error details.")

    else:
        _hoc2swc(hoc_path, mod_path, swc_path, no_mod)




