import os
import PyInstaller.__main__

def build_exe(py_script,
              one_file=True,
              no_console=True,
              icon=True,
              version=True):

    command = []

    # file to build
    command.append('pyinstaller ' + os.path.abspath(os.getcwd() + r'\Scripts\\' + py_script + '.py'))
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
    if version:
        command.append('--version-file=' + os.getcwd() + r'\version.txt')

    command.append('--clean')

    PyInstaller.__main__.run(command)

first = r'pyinstaller C:\Users\Brand\PycharmProjects\Westeros\Scripts\Scripts\Test.py.py --distpath=C:\Users\Brand\PycharmProjects\Westeros\Scripts\dist --workpath=C:\Users\Brand\PycharmProjects\Westeros\Scripts\build --onefile --noconsole --icon=C:\Users\Brand\PycharmProjects\Westeros\Scripts\icon.ico --version-file=C:\Users\Brand\PycharmProjects\Westeros\Scripts\version.txt --clean'

result = build_exe('Test')

[print(r) for r in result]





