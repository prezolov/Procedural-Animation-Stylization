import maya.cmds as cmds
import maya.mel as mel
import math
from functools import partial
framesPosed = []
init = []#True
nextLoop = []
next = [] # Holds the value of the next keyframe
keyable = []
# https://www.desmos.com/calculator/hamwkcp1rh
def CalculatePos(x, n):
    #decimal.normalize(x)
    #print(str(x))
    #x*=0.01
    #position = math.pow((1 - math.cos(x)), n)
    position = (1 - x) ** n
    #position = 0.9 ** n
    print("x is: " + str(x))
    #position = math.pow(1 - math.cos(math.pi/2 - x), n)
    return position

def NormalizeKey(interpolationKeyframe, firstKeyFrame, lastKeyFrame):
    return (interpolationKeyframe - firstKeyFrame) / (lastKeyFrame - firstKeyFrame)
    #return interpolationKeyframe * (lastKeyFrame - firstKeyFrame) + firstKeyFrame

def DeleteButtonPush(time, *args):
    global framesPosed
    global nextLoop
    # Remove the given frame from the framesPosed list.
    for i in range(0, len(framesPosed)):
        if (framesPosed[i] == time):
            
            framesPosed.remove(time)
            #nextLoop.pop(i)
            print(str(time) + " was removed.")

    # Remove the UI parts
    cmds.deleteUI('stylize'+ str(int(time)))
    cmds.deleteUI('delete'+ str(int(time)))
    # This will also delete the children
    cmds.deleteUI('pose'+ str(int(time)))

    # TODO: Code to actually remove the keyframes

    #print("time associated with button pressed: " + str(time))

def SavePoseButtonPush(*args):
    
    # This is the initial inWeight of each Key Tangent
    selected = []
    selected = cmds.ls(sl=1)
    # User did not select anything, issue warning.
    if len(selected) < 1:
        cmds.warning("No object selected.")
        cmds.confirmDialog(title="Warning", message = "No object selected.")
    else:
        #print(initIW)
        print("Pose saved...")
        
        global framesPosed
        alreadyPosed = False
        #print("Frames posed: ")
        #print(framesPosed)
        for i in range(0, len(framesPosed)):
            if cmds.currentTime(query=True) == framesPosed[i]:
                print("This frame has already been posed, updating")
                alreadyPosed = True
        
        if alreadyPosed == False:
            # Add current frame to the array of frames that have been posed
            # Adds to end of array
            framesPosed.insert(len(framesPosed), cmds.currentTime(query=True))
            #print(framesPosed)
            #cmds.text( label='Pose at frame: ' + str(cmds.currentTime( query=True )), bgc=[1,0,0])
            
            #cmds.columnLayout( adjustableColumn=True )
            cmds.rowLayout( numberOfColumns=2, adjustableColumn=1)
            cmds.checkBox('stylize' + str(int(cmds.currentTime( query=True ))), label='Stylize', bgc=[0.75,0.7,0.7], v = True )

            cmds.button('delete' + str(int(cmds.currentTime( query=True ))),label='Delete Pose', bgc=[0.75,0.7,0.7], command = partial(DeleteButtonPush, cmds.currentTime(query=True)))

            cmds.setParent( '..' )
            cmds.frameLayout('pose' + str(int(cmds.currentTime( query=True ))), label='Pose at frame: ' + str(cmds.currentTime( query=True )), labelAlign='top', cll = True, cl = True )
            global keyable
            keyable = cmds.listAttr(cmds.ls(sl=1), k=True)
            for i in range(0, len(keyable)):
                if i == 2:
                    cmds.checkBox(keyable[i] + str(int(cmds.currentTime( query=True ))), label=keyable[i], v = True )
                else:
                    cmds.checkBox(keyable[i] + str(int(cmds.currentTime( query=True ))), label=keyable[i], v = False )
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))))
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))), edit = True, enable = False, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))

        else:
            keyable = cmds.listAttr( cmds.ls(sl=1), k=True)  
            for i in range(0, len(keyable)):
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))), edit = True, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))
        cmds.setParent( '..' )

def slider_drag_callback(*args):
    #print("Slider Dragged")
    global framesPosed
    #print(framesPosed)
     #cmds.currentTime( query=True )
    for i in range(0, len(framesPosed)):
        currentKeyFrame = framesPosed[i]
        if cmds.checkBox('stylize' + str(int(framesPosed[i])), q = True, value = True) == True:
            global next
            global init
            #print(i)
            #print(len(init))
            if(i == len(init)):
                init.insert(i, True)

            if init[i] == True: 
                next.insert(i, cmds.findKeyframe(cmds.ls(sl=1), time=(currentKeyFrame,currentKeyFrame), which="next"))
                init[i] = False
            global keyable
            # Go through each keyable attribute
            for attribute in range(0, len(keyable)):
                # For each check box that is checked
                if cmds.checkBox(keyable[attribute] + str(int(framesPosed[i])), q = True, value = True) == True:
                    
                    #print(keyable)
                    # Get value of currentKeyFrame
                    currentKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (currentKeyFrame, currentKeyFrame), at = keyable[attribute])
                    nextKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (next[i], next[i]), at = keyable[attribute])

                    distance = nextKeyFrameVal[0] - currentKeyFrameVal[0]
                    maxY = 0
                    minY = 0
                    # Used for 'de-normalization'
                    #if (distance > 0):
                    #    maxY = nextKeyFrameVal[0]
                    #    minY = currentKeyFrameVal[0]
                    #else:
                    maxY = currentKeyFrameVal[0]
                    minY = nextKeyFrameVal[0]

                    #print(currentKeyFrameVal)
                    print("distance is: " + str(distance))
                    
                    key2 = (currentKeyFrame + next[i]) / 2 # 0.5
                    key1 = (currentKeyFrame + key2) / 2 # 0.25
                    key5 = (currentKeyFrame + key1) / 2 # 0.125
                    key3 = (key2 + next[i]) / 2 # 0.75
                    key4 = (key3 + next[i]) / 2 # 0.875
                    key6 = (key4 + next[i]) / 2 # 0.9375

                    valueFromSlider = cmds.floatSliderGrp('float', query=True, value = 1)
                    #print("value from slider is: " + str(valueFromSlider))
                    #print("key1 is: " + str(key1), ", normalized: " + str(NormalizeKey(key1, currentKeyFrame, next[i])))
                    #print("key2 is: " + str(key2), ", normalized: " + str(NormalizeKey(key2, currentKeyFrame, next[i])))
                    #print("key3 is: " + str(key3), ", normalized: " + str(NormalizeKey(key3, currentKeyFrame, next[i])))
                   
                    # Normalize the keyframes
                    normalKey1 = NormalizeKey(key1, currentKeyFrame, next[i])
                    normalKey2 = NormalizeKey(key2, currentKeyFrame, next[i])
                    normalKey3 = NormalizeKey(key3, currentKeyFrame, next[i])
                    normalKey4 = NormalizeKey(key4, currentKeyFrame, next[i])
                    normalKey5 = NormalizeKey(key5, currentKeyFrame, next[i])
                    normalKey6 = NormalizeKey(key6, currentKeyFrame, next[i])

                    print("key1 is: " + str(key1), ", normalized: " + str(normalKey1))
                    print("key2 is: " + str(key2), ", normalized: " + str(normalKey2))
                    print("key3 is: " + str(key3), ", normalized: " + str(normalKey3))
                    print("key4 is: " + str(key4), ", normalized: " + str(normalKey4))

                    #print("key1 is: " + str(key1))
                    #print("key2 is: " + str(key2))
                    #print("key3 is: " + str(key3))
                    #print("CalculatePos for key1: " + str(CalculatePos(normalKey1, valueFromSlider)))
                    #print("CalculatePos for key2: " + str(CalculatePos(normalKey2, valueFromSlider)))
                    #print("CalculatePos for key3: " + str(CalculatePos(normalKey3, valueFromSlider)))
                    #print("CalculatePos for key4: " + str(CalculatePos(normalKey4, valueFromSlider)))
                    # Set the keyframe values (For some reason, adding the value of normalKey3 as an input value to the CalculatePos function, 
                    # for the frame key1 and vice versa, makes the system behave in the way originally expected.)
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalKey1, valueFromSlider) * (maxY - minY) + minY, t = (key1, key1), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalKey2, valueFromSlider) * (maxY - minY) + minY, t = (key2, key2), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalKey3, valueFromSlider) * (maxY - minY) + minY, t = (key3, key3), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalKey4, valueFromSlider) * (maxY - minY) + minY, t = (key4, key4), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalKey5, valueFromSlider) * (maxY - minY) + minY, t = (key5, key5), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalKey6, valueFromSlider) * (maxY - minY) + minY, t = (key6, key6), itt = "spline", ott = "spline" )
                    
                    #if distance > 0:
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key1, valueFromSlider) * distance - distance / 1.5, t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key2, valueFromSlider) * distance - distance / 3, t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key3, valueFromSlider) * distance - distance / 4, t = (key3, key3), itt = "spline", ott = "spline" )
                        
                         
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey3, valueFromSlider) * distance, t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey2, valueFromSlider) * distance, t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey1, valueFromSlider) * distance, t = (key3, key3), itt = "spline", ott = "spline" )
                   #else:
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key1, valueFromSlider) * (-distance) + distance / 4, t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key2, valueFromSlider) * (-distance) + distance / 3, t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key3, valueFromSlider) * (-distance) + distance / 1.5, t = (key3, key3), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey1, valueFromSlider) * (distance), t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey2, valueFromSlider) * (distance), t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey3, valueFromSlider) * (distance), t = (key3, key3), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=calculatePos(key2, valueFromSlider) * (-distance), t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=calculatePos(key3, valueFromSlider) * (-distance) - (currentKeyFrameVal[0] - distance)/4, t = (key3, key3), itt = "spline", ott = "spline" )


# Make a new window
window = cmds.window( title="Animation Stylization", iconName='Short Name', widthHeight=(500, 500), sizeable = True)
# Assign a layout
cmds.columnLayout( adjustableColumn=True )
# Add a button
cmds.button( label='Save Pose', command=SavePoseButtonPush)

cmds.floatSliderGrp('float', label='Stylization Value', field=True, minValue=0.0, maxValue=30.0, fieldMinValue=0.0, fieldMaxValue=30.0, value=0, dc=slider_drag_callback)

# Show the window
cmds.showWindow( window )