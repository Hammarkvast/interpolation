import os
import numpy as np
import re
from collections import OrderedDict

input = []
directory = 'dataset/train/test'

'''
Grabs the data from each of the files and adds them to a dictionary.
'''
def getManualAnnotations(dir, store):
    dict = OrderedDict()
    for filename in os.listdir(dir):
        file = open (dir + '/' + filename, 'r')
        [frame] = re.findall(r'\d+', filename)
        for line in file:
            newline = line.strip().split(" ")
            store.append(newline)
        dict[int(frame)] = store
        store = []
    return dict


'''
Goes through a store containing the manually annotated frames, and
returns a list containing the pairs where an interpolation can be done. 
'''
def setInterpolationPairs(store):
    pairs = []
    for frame in store:
        if (frame + 1) in store:
            continue
        elif store.index(frame) == (len(store) -1):
            break
        else:
            validFrame = store[store.index(frame) + 1]
            validPair = (frame, validFrame)
            pairs.append(validPair)
    return pairs

'''
Prepares for interpolation by taking an interpolation pair, and then grabbing the corresponding manual annotations for each
pair and then sending that, along with the frame that wants an automatic annotation to the function that does the interpolation.
'''

def prepareInterpolation(listOfPairs, dictionary):
    for pair in listOfPairs:
        startFrame = pair[0]
        currentFrame = pair[0] + 1
        endFrame = pair[1]
        while currentFrame < endFrame:
            startBoxes = dictionary.get(startFrame).copy()
            endBoxes = dictionary.get(endFrame).copy()
            interpolateCoordinates(startBoxes, endBoxes, startFrame, currentFrame, endFrame)
            currentFrame+=1
'''
Does the interpolation for a specific frame (interpolateFrame) by making sure that we are doing the interpolation between two
annotations that are annotating the same class, and then sending the interpolated values to a function that writes everything to a file.
'''

def interpolateCoordinates(startLabels, endLabels, firstFrame, interpolateFrame, lastFrame):
    frames = [firstFrame, lastFrame]
    auto = []
    for startIndex, _ in enumerate(startLabels):
        for endIndex, _ in enumerate(endLabels):
            if startLabels[startIndex][0] == endLabels[endIndex][0]:
                x = np.interp(interpolateFrame, frames, [float(startLabels[startIndex][1]), float(endLabels[endIndex][1])])
                y = np.interp(interpolateFrame, frames, [float(startLabels[startIndex][2]), float(endLabels[endIndex][2])])
                w = np.interp(interpolateFrame, frames, [float(startLabels[startIndex][3]), float(endLabels[endIndex][3])])
                h = np.interp(interpolateFrame, frames, [float(startLabels[startIndex][4]), float(endLabels[endIndex][4])])
                annotation = [startLabels[startIndex][0], x, y, w, h]
                endLabels.pop(endIndex)
                auto.append(annotation)
                break
    createLabelFile(auto, interpolateFrame)

def createLabelFile(box_annotations, nameOfFrame): 
    frameFile = open(directory + '/' + "frame" + str(nameOfFrame) + ".txt", 'w')
    for annotation in box_annotations:
        frameFile.write(str(annotation[0]) + " " + str(annotation[1])+ " " + str(annotation[2]) + " " + str(annotation[3]) + " " + str(annotation[4]) + '\n') 
    frameFile.close()


# test = [1,4,6,7,8,10]
dictionary = getManualAnnotations(directory, input)
sortedDict = sorted(dictionary)
pair = setInterpolationPairs(sortedDict)
prepareInterpolation(pair, dictionary)

# match = re.match(r"[a-z]+([0-9]+)", 'frame3500.txt', re.I)
# if match:
#     items = match.groups()
# print(items[0])

# [s] = re.findall(r'\d+', 'frame3500.txt')
# print(s)