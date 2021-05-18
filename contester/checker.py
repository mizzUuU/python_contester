from .models import *
import subprocess
import os


def getTests(taskId):
    pass


def checker(document, taskId):
    # copying file to cheker path
    currentPath = "media/tests/" + str(taskId)+'/'
    checkerPath = currentPath + "myAwesomeCode.py"
    with open(checkerPath, 'wb') as actual_file:
        actual_file.write(document.read())
    # starting script
    subprocess.check_call([currentPath+'/test.sh', 'python3 ' + checkerPath, currentPath])
    text_file = open(currentPath+"result.txt", "r")
    lines = text_file.readlines()
    print(lines)
    print(len(lines))
    text_file.close()

    result = []
    for to in lines:
        if to == "OK\n":
            result.append(1)
        else:
            result.append(0)
    return result