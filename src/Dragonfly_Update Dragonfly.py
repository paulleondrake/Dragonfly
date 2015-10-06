#
# Dragonfly: A Plugin for Climate Data Generation (GPL) started by Chris Mackey
# 
# This file is part of Dragonfly.
# 
# Copyright (c) 2015, Chris Mackey <Chris@MackeyArchitecture.com> 
# Dragonfly is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Dragonfly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Code Developers and Beta Testers of new Dragonfly components can use this component to remove old Dragonfly components, add new Dragonfly components, and update existing Dragonfly components from a synced Github folder on their computer.
This component can also update outdated Dragonfly components in an old Grasshopper file so long as the updates to the components do not involve new inputs or outputs.
-
Provided by Dragonfly 0.0.60
    
    Args:
        sourceDirectory_: An optional address to a folder on your computer that contains the updated Dragonfly userObjects. If no input is provided here, the component will download the latest version from GitHUB.
        _updateThisFile: Set to "True" if you want this component to search through the current Grasshopper file and update Dragonfly components that have changed.
        _updateAllUObjects: Set to "True" to sync all the Dragonfly userObjects in your Grasshopper folder with the GitHUB.
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Dragonfly_Update Dragonfly"
ghenv.Component.NickName = 'updateDragonfly'
ghenv.Component.Message = 'VER 0.0.60\nSEP_19_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "4 | Developers"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import shutil
import zipfile
import time
import urllib
import Grasshopper.Folders as folders
import System

def downloadSourceAndUnzip(lb_preparation):
    """
    Download the source code from github and unzip it in temp folder
    """
    url = "https://github.com/chriswmackey/Dragonfly/archive/master.zip"
    targetDirectory = os.path.join(sc.sticky["Dragonfly_DefaultFolder"], "dragonflySrc")
    
    # download the zip file
    print "Downloading the source code..."
    zipFile = os.path.join(targetDirectory, os.path.basename(url))
    
    # if the source file is just downloded then just use the available file
    if os.path.isfile(zipFile) and time.time() - os.stat(zipFile).st_mtime < 1000: download = False
    else:
        download = True
        try:
            lb_preparation.nukedir(targetDirectory, True)
        except:
            pass
    
    # create the target directory
    if not os.path.isdir(targetDirectory): os.mkdir(targetDirectory)

    if download:
        try:
            client = System.Net.WebClient()
            client.DownloadFile(url, zipFile)
            if not os.path.isfile(zipFile):
                print "Download failed! Try to download and unzip the file manually from:\n" + url
                return
        except Exception, e:
            print `e` + "\nDownload failed! Try to download and unzip the file manually from:\n" + url
            return
    
    #unzip the file
    with zipfile.ZipFile(zipFile) as zf:
        for f in zf.namelist():
            if f.endswith('/'):
                try: os.makedirs(f)
                except: pass
            else:
                zf.extract(f, targetDirectory)
    
    userObjectsFolder = os.path.join(targetDirectory, r"dragonfly-master\userObjects")
    
    return userObjectsFolder

def getAllTheComponents(onlyGHPython = True):
    components = []
    
    document = ghenv.Component.OnPingDocument()
    
    for component in document.Objects:
        if onlyGHPython and type(component)!= type(ghenv.Component):
            pass
        else:
            components.append(component)
    
    return components

def updateTheComponent(component, newUOFolder, lb_preparation):
    
    def isNewerVersion(currentUO, component):
        """
        check if the component has a newer version than the current userObjects
        """
        # get the code insider the userObject
        ghComponent = currentUO.InstantiateObject()
        
        # version of the connected component
        if component.Message == None:
            return True, ghComponent.Code
        if len(component.Message.split("\n"))<2:
            return True, ghComponent.Code
        
        ghVersion, ghDate = component.Message.split("\n")
        ghCompVersion = map(int, ghVersion.split("VER ")[1].split("."))
        month, day, ghYear  = ghDate.split("_")
        # print version, date
        month = lb_preparation.monthList.index(month.upper()) + 1
        ghCompDate = int(lb_preparation.getJD(month, day))
        
        # this is not the best way but works for now!
        # should be a better way to compute the component and get the message
        componentCode = ghComponent.Code.split("\n")
        UODate = ghCompDate - 1
        # version of the file
        for lineCount, line in enumerate(componentCode):
            if lineCount > 200: break
            if line.strip().startswith("ghenv.Component.Message"):
                #print line
                # print line.split("=")[1].strip().split("\n")
                version, date = line.split("=")[1].strip().split("\\n")
                
                # in case the file doesn't have an standard Dragonfly message let it be updated
                try:
                    UOVersion = map(int, version.split("VER ")[1].split("."))
                except Exception, e:
                    return True, ghComponent.Code
                month, day, UOYear  = date.split("_")
                month = lb_preparation.monthList.index(month.upper()) + 1
                UODate = int(lb_preparation.getJD(month, day))
                break
        
        # check if the version of the code is newer
        if int(ghYear.strip()) < int(UOYear[:-1].strip()):
                return True, ghComponent.Code
        elif ghCompDate < UODate:
            return True, ghComponent.Code
        elif ghCompDate == UODate:
            for ghVer, UOVer in zip(UOVersion, UOVersion):
                if ghVer > UOVer: return False, " "
            return True, ghComponent.Code
        else:
            return False, " "
    
    # check if the userObject is already existed in the folder
    try:
        filePath = os.path.join(newUOFolder, component.Name + ".ghuser")
        newUO = gh.GH_UserObject(filePath)
    except:
        # there is no newer userobject with the same name so just return
        return
    
    # if is newer remove
    isNewer, newCode = isNewerVersion(newUO, component)
    # replace the code inside the component with userObject code
    if isNewer:
        component.Code = newCode
        component.ExpireSolution(True)
    

def main(sourceDirectory, updateThisFile, updateAllUObjects):
    if not sc.sticky.has_key('dragonfly_release'): return "You need to let Dragonfly fly first!", False
    if not sc.sticky.has_key('ladybug_release'): return "You need to let Ladybug fly first!", False
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    if sourceDirectory == None:
        userObjectsFolder = downloadSourceAndUnzip(lb_preparation)
        if userObjectsFolder==None: return "Download failed! Read component output for more information!", False
    else:
        userObjectsFolder = sourceDirectory
    
    destinationDirectory = folders.ClusterFolders[0]
    
    if updateThisFile:
        # find all the userObjects
        ghComps = getAllTheComponents()
        
        # for each of them check and see if there is a userObject with the same name is available
        for ghComp in ghComps:
            if ghComp.Name != "Dragonfly_Update Dragonfly":
                updateTheComponent(ghComp, userObjectsFolder, lb_preparation)
        
        return "Done!", True
        
    # copy files from source to destination
    if updateAllUObjects:
        if not userObjectsFolder  or not os.path.exists(userObjectsFolder):
            warning = 'source directory address is not a valid address!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        srcFiles = os.listdir(userObjectsFolder)
        print 'Removing Old Version...'
        # remove userobjects that are currently removed
        fileNames = os.listdir(destinationDirectory)
        for fileName in fileNames:
            # check for ladybug userObjects and delete the files if they are not
            # in source anymore
            if fileName.StartsWith('Dragonfly') and fileName not in srcFiles:
                fullPath = os.path.join(destinationDirectory, fileName)
                os.remove(fullPath)                

        print 'Updating...'
        
        for srcFileName in srcFiles:
            # check for ladybug userObjects
            if srcFileName.StartsWith('Dragonfly'):
                srcFullPath = os.path.join(userObjectsFolder, srcFileName)
                dstFullPath = os.path.join(destinationDirectory, srcFileName) 
                
                # check if a newer version is not aleady exist
                if not os.path.isfile(dstFullPath): shutil.copy2(srcFullPath, dstFullPath)
                # or is older than the new file
                elif os.stat(srcFullPath).st_mtime - os.stat(dstFullPath).st_mtime > 1: shutil.copy2(srcFullPath, dstFullPath)
        
        return "Done!" , True

if _updateThisFile or _updateAllUObjects:
    msg, success = main(sourceDirectory_, _updateThisFile, _updateAllUObjects)
    if not success:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    else:
        print msg
else:
    print " "