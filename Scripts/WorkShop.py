import os
import sys
import shutil
import numpy as np
import pandas as pd
from pathlib import Path
from time import strftime
import PyInstaller.__main__


def build_exe(script='',
              description='',
              new_rendition=False,
              new_release=False,
              new_edition=False,
              one_file=True,
              no_console=True,
              icon=True):

    os.chdir(os.path.dirname(os.getcwd()))

    if script == '':
        print('There was no script to build.')
        quit()

    dtypes = {'Script': 'str',
              'Edition': 'int',
              'Release': 'int',
              'Rendition': 'int',
              'Build': 'int',
              'Version': 'float',
              'Description': 'str'}

    # Retrieving the version information
    try:
        hist = pd.read_csv(r'BuildHistory.csv', index_col=0, dtype=dtypes)
    except FileNotFoundError:
        # In case their is no previous build history file
        np_dtypes = {'str': str, 'int': int, 'float': float}
        hist = np.empty((0,), dtype=[(k, np_dtypes[v]) for k, v in dtypes.items()])
        hist = pd.DataFrame(hist)

    whist = hist[hist.Script == script]
    ver_list = ['', '', '', '']

    try:
        whist = whist[whist.Version == max(whist.Version)].reset_index(drop=True)

    except ValueError:  # For if data frame is empty
        whist = whist.append({'Script': script,
                              'Edition': 0,
                              'Release': 0,
                              'Rendition': 0,
                              'Build': 0,
                              'Version': 0,
                              'Description': 'Zeroth Build'},
                             ignore_index=True)
        pass

    if new_edition or new_release or new_rendition:
        if new_rendition:
            ver_list[0] = whist.Edition[0]
            ver_list[1] = whist.Release[0]
            ver_list[2] = whist.Rendition[0] + 1
            ver_list[3] = whist.Build[0]
        elif new_release:
            ver_list[0] = whist.Edition[0]
            ver_list[1] = whist.Release[0] + 1
            ver_list[2] = whist.Rendition[0]
            ver_list[3] = whist.Build[0]
        else:  # new edition
            ver_list[0] = whist.Edition[0] + 1
            ver_list[1] = whist.Release[0]
            ver_list[2] = whist.Rendition[0]
            ver_list[3] = whist.Build[0]
    else:  # new build
        ver_list[0] = whist.Edition[0]
        ver_list[1] = whist.Release[0]
        ver_list[2] = whist.Rendition[0]
        ver_list[3] = whist.Build[0] + 1

    ver_list = [str(i) for i in ver_list]
    ver_list[1] = format(int(ver_list[1]), '02')

    data = {'Script': [script],
            'Edition': [ver_list[0]],
            'Release': [int(ver_list[1])],
            'Rendition': [ver_list[2]],
            'Build': [ver_list[3]],
            'Version': [float(''.join(ver_list))],
            'Description': [description]
            }

    new_entry = pd.DataFrame.from_dict(data=data, orient='columns').reset_index(drop=True)

    hist = hist.append(new_entry, sort=False).reset_index(drop=True)

    try:
        hist.to_csv(r'BuildHistory.csv')

    except PermissionError:
        print('History file not accessible, could not update Build History.')
        quit()

    # Making the version information file
    ver_list = [str(int(i)) for i in ver_list]

    company_name = ''
    legal_copyright = ' ' + company_name + '. All rights reserved.'
    product_name = '' + script
    product_version = ver_list[0] + '.' + ver_list[1] + '.' + ver_list[2] + '.' + ver_list[3]
    file_version = product_version + ' (win7sp1_rtm.101119-1850)'

    lines = [
        'VSVersionInfo(\n',
        '  ffi=FixedFileInfo(\n',
        '    filevers=(' + ver_list[0] + ', ' + ver_list[1] + ', ' + ver_list[2] + ', ' + ver_list[3] + '),\n',
        '    prodvers=(' + ver_list[0] + ', ' + ver_list[1] + ', ' + ver_list[2] + ', ' + ver_list[3] + '),\n',
        '    mask=0x3f,\n',
        '    flags=0x0,\n',
        '    OS=0x40004,\n',
        '    fileType=0x1,\n',
        '    subtype=0x0,\n',
        '    date=(0, 0)\n',
        '    ),\n',
        '  kids=[\n',
        '    StringFileInfo(\n',
        '      [\n',
        '      StringTable(\n',
        '        u\'040904B0\',\n',
        '        [StringStruct(u\'CompanyName\', u\'' + company_name + '\'),\n',
        '        StringStruct(u\'FileDescription\', u\'' + build_description + '\'),\n',
        '        StringStruct(u\'FileVersion\', u\'' + file_version + ' (win7sp1_rtm.101119-1850)\'),\n',
        '        StringStruct(u\'InternalName\', u\'cmd\'),\n',
        '        StringStruct(u\'LegalCopyright\', u\'\\xa9 ' + legal_copyright + '\'),\n',
        '        StringStruct(u\'OriginalFilename\', u\'' + script + '\'),\n',
        '        StringStruct(u\'ProductName\', u\'' + product_name + '\'),\n',
        '        StringStruct(u\'ProductVersion\', u\'' + product_version + '\')])\n',
        '      ]), \n',
        '    VarFileInfo([VarStruct(u\'Translation\', [1033, 1200])])\n',
        '  ]\n',
        ')',
    ]

    version_info = open(r'version.txt', 'w')

    for line in lines:
        version_info.write(line)

    version_info.close()

    # Building the exe file
    command = list()

    # file to build
    command.append(os.path.abspath(os.getcwd() + r'\Scripts\\' + script + '.py'))

    # destination path
    command.append('--distpath=' + os.getcwd() + r'\dist')

    # working directory
    command.append('--workpath=' + os.getcwd() + r'\build')

    if one_file:
        command.append('--onefile')
    if no_console:
        command.append('--noconsole')
    if icon:
        command.append('--icon=' + os.getcwd() + r'\icon.ico')
    if version_info:
        command.append('--version-file=' + os.getcwd() + r'\version.txt')

    command.append('--clean')

    PyInstaller.__main__.run(command)

    # Moving the build files and exe
    time = strftime("%Y%m%d-%H%M%S")

    # Creates the out path as a string
    builds_folder = os.getcwd().replace("\\", r'\\') + r'\\' + 'Builds' + r'\\' + script
    target_folder = builds_folder + r'\\' + time + r'\\'

    # Creates the Builds folder if it doesn't already exist
    #  This will house all builds of all scripts
    if not os.path.exists(builds_folder):
        os.makedirs(builds_folder)

    # Makes the folder that will contain the build and supporting files
    os.makedirs(target_folder)

    # Moving the two temporary folders to the version folder
    for Output in [r'\\build\\', r'\\dist']:
        shutil.move(src=os.getcwd() + Output, dst=target_folder + Output)

    # Moving the spec file
    shutil.move(src=os.getcwd() + r'\\Scripts\\' + script + '.spec',
                dst=target_folder + script + '.spec')

    # Moving the temp files into the build folder
    for file in os.listdir(target_folder + r'build\\' + script):
        source = target_folder + r'build\\' + script + r'\\' + file
        shutil.move(src=source, dst=target_folder + r'build\\')

    # Removes the empty build folder
    shutil.rmtree(target_folder + r'build\\' + script + r'\\')

    # Moves the exe file
    source = target_folder + r'dist\\' + script + '.exe'
    shutil.move(src=source, dst=target_folder)

    # Removes the empty dist folder
    shutil.rmtree(target_folder + r'dist\\')

    return target_folder + r'\\' + script + '.exe'


if __name__ == '__main__':

    Scripts = [Path(f).stem for f in os.listdir(os.getcwd())]
    scriptDict = {Scripts.index(s): s for s in Scripts}

    print("{:<8} {:<15}".format('Index', 'Script'))

    for k, v in scriptDict.items():
        print("{:<8} {:<10}".format(k, v))

    ans = ''
    inIndex = True
    while isinstance(ans, str) or not inIndex:
        ans = input('\nEnter index of script to build, or enter x to terminate.\nIndex must be an integer.\n')
        if ans == 'x':
            print('Script terminated.')
            try:
                exit()
            except NameError:
                sys.exit()
        try:
            ans = int(ans)
            inIndex = 0 <= ans < len(Scripts)
        except ValueError:
            pass

    build_description = input('Build description:\n')

    run_after = input('Start exe after build? (Y/N)\n').upper() == 'Y'

    print('Building', Scripts[ans]+'.py')

    exe = build_exe(script=Scripts[ans], description=build_description)

    print('Build successful:', Scripts[ans] + '.exe')

    if run_after:
        os.system('start ' + exe)
