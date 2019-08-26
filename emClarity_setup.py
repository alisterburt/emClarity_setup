import os
import sys
import getopt

# Usage
usage = """
USAGE: emClarity_setup.py -i <IMOD_BASE_DIR> -o <EMCLARITY_PROJECT_DIR>
    Argument                 Input                      Explanation
    -i                       <IMOD_BASE_DIR>            Directory containing all tilt-series reconstructed in IMOD
    -o                       <EMCLARITY_PROJECT_DIR>    emClarity project directory, necessary files will be copied here
    
    Requires IMOD programs to be on the system path
"""

if len(sys.argv) > 1:
    options, remainder = getopt.getopt(sys.argv[1:], 'i:o')

    for opt, arg in options:
        if opt == '-i':
            IMOD_BASE_DIR = arg
        elif opt == '-o':
            EMCLARITY_PROJECT_DIR = arg

    print('Running reconstruct_tomos.py using command line arguments...')
    print('Directory containing all IMOD files: {}'.format(IMOD_BASE_DIR))
    print('Directory for preparation of emClarity project: {}'.format(EMCLARITY_PROJECT_DIR))
else:
    print(usage)
    print('Desisting...')
    sys.exit()


# Define functions
# Get all edf files in specific directory recursively
def get_edf_files(directory):
    """Gets list of all .edf files in a directory or any subdirectory
    (basenames for IMOD alignment projects)
    """
    edf_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.edf'):
                edf_files.append(os.path.join(root, file))

    return edf_files

class imod_project_dir:
    """A class for imod project directories which helps to generate necessary filenames related to
    imod TS alignment projects.
    """
    def __init__(self, edf_file):
        # Basic info
        self.edf_file = edf_file
        self.directory = os.path.abspath(os.path.dirname(edf_file))
        self.basename = os.path.basename(edf_file).split('.')[0]

        # Files for reconstruction of tilt series
        self.aligned_stack = self.basename + '.ali'
        self.tilt_angles = self.basename + '.tlt'
        self.fiducial_model = self.basename + '.fid'

        # Files for Generation of aligned stack
        self.raw_stack = self.basename + '.st'
        self.xf = self.basename + '.xf'
        self.local_alignments = self.basename + 'local.xf'
        self.erase_fiducials = self.basename + '_erase.fid'


def emClarity_project_setup(project_directory, edf_files):
    # Make necessary directories
    fixedStacks_dir = os.path.join(project_directory, 'fixedStacks')
    os.makedirs(fixedStacks_dir, exist_ok=True)

    # Make imod project directory object for each edf file
    imod_projects = [imod_project_dir(edf_file) for edf_file in edf_files]

    # collect files from projects for emClarity
    tilt_angles_files_imod = [os.path.join(imod_project.directory, imod_project.tilt_angles)
                         for imod_project in imod_projects]

    xf_files_imod = [os.path.join(imod_project.directory, imod_project.xf)
                for imod_project in imod_projects]

    local_alignment_files_imod = [os.path.join(imod_project.directory, imod_project.local_alignments)
                             for imod_project in imod_projects]

    erase_fid_files_imod = [os.path.join(imod_project.directory, imod_project.erase_fiducials)
                       for imod_project in imod_projects]

    raw_stacks_imod =[os.path.join(imod_project.directory, imod_project.raw_stack) for imod_project in imod_projects]


    # set corresponding output filenames in emClarity project dir
    tilt_angles_files_emC = [os.path.join(fixedStacks_dir, imod_project.tilt_angles)
                             for imod_project in imod_projects]

    xf_files_emC = [os.path.join(fixedStacks_dir, imod_project.xf)
                    for imod_project in imod_projects]

    local_alignment_files_emC = [os.path.join(fixedStacks_dir, imod_project.basename + '.local')
                                 for imod_project in imod_projects]

    erase_fid_files_emC = [os.path.join(fixedStacks_dir, imod_project.basename + '.erase')
                           for imod_project in imod_projects]

    raw_stacks_emC = [os.path.join(fixedStacks_dir, imod_project.basename + '.fixed')
                      for imod_project in imod_projects]


    def run(command):
        """print and run system command"""
        print(command)
        os.system(command)

    # Assemble commands for copying & setting up
    basenames = []
    for idx, project in enumerate(imod_projects):
        commands = []
        tmp_model_file = os.path.join(project.directory, 'tmp.mod')
        tilt_angles = 'cp -v {} {}'.format(tilt_angles_files_imod[idx], tilt_angles_files_emC[idx])
        xf_files = 'cp -v {} {}'.format(xf_files_imod[idx], xf_files_emC[idx])
        local_alignment_files = 'cp -v {} {}'.format(local_alignment_files_imod[idx], local_alignment_files_emC[idx])
        erase_fid_files = 'cp -v {} {}'.format(erase_fid_files_imod[idx], erase_fid_files_emC[idx])
        raw_stacks = 'cp -v {} {}'.format(raw_stacks_imod[idx], raw_stacks_emC[idx])
        imodtrans = 'imodtrans -i {} {} {}'.format(raw_stacks_emC[idx], erase_fid_files_emC[idx], tmp_model_file)
        model2point = 'model2point -float {} {}'.format(tmp_model_file, erase_fid_files_emC[idx] + '2')
        rm_tmp_mod = 'rm -vf {}'.format(tmp_model_file)

        commands.append(tilt_angles)
        commands.append(xf_files)
        commands.append(local_alignment_files)
        commands.append(erase_fid_files)
        commands.append(raw_stacks)
        commands.append(imodtrans)
        commands.append(model2point)
        commands.append(rm_tmp_mod)

        basenames.append(project.basename)

        print('Preparing files for project number "{}" with name "{}"...'.format(idx, project.basename))
        print('Running commands...')
        for command in commands:
            run(command)

    # Write out a file with basenames for easier time calling emClarity later
    basename_file = os.path.join(EMCLARITY_PROJECT_DIR, 'basenames.txt')
    with open(basename_file, mode='wt', encoding='utf8') as file:
        file.write('\n'.join(basenames))

# Running
edf_files = get_edf_files(IMOD_BASE_DIR)
emClarity_project_setup(EMCLARITY_PROJECT_DIR, edf_files)

