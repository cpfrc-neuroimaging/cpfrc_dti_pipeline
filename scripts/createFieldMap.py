##### This script has functions that will:
# 1) generate a list of all the subjects that have been processed on new scanner software
# 2) copy over abcd bvec and bval files 
# 3) create fieldmaps using external fsl script
# 4) verify that the fieldmaps have been successfully created

import sys
import os
import shutil
import time


dtiProc = "/PROJECTS/REHARRIS/explosives/dtiProc"
rawDir = "/PROJECTS/REHARRIS/explosives/raw/"
niiPath = "/DTI"

# verify that all the necessary modules have been loaded

def verifyModules():
	print("Modules loaded:")
	os.system("module list")
	while True:
			loaded = input(f"\n{bcolors.WARNING}For this script, you need the fsl module loaded.\nIs it listed above? If so, type yes and hit enter. \nIf not, please type no and hit enter.\n{bcolors.ENDC}")
			if loaded == "yes" or loaded == "y" or loaded == "Yes" or loaded == "YES":
				print("great! running script...")
				break
			elif loaded == "no" or loaded == "n" or loaded == "No" or loaded == "NO":
				print("\nplease load fsl using the following command:\n")
				print("module load fsl/6.0.3\n")
				print("after loading the module, relaunch the script")
				sys.exit()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# get a list of all the subjects that have been processed with the new software

def getSubList(rawDir):
	os.chdir(rawDir)
	subList = []
	for sub in os.listdir():
		os.chdir(sub)
		if os.path.isdir("DTI"):
			os.chdir("DTI")
			if os.path.isfile("dti.nii"):
				subList.append(sub)
		os.chdir(rawDir)
	return subList


## copies the abcd bvec and bval files

def changeBVFiles(rawDir, subList):
	os.chdir(rawDir)
	for sub in subList:
		os.chdir(sub + niiPath)
		if os.path.isfile("abcd_edit.bval") and os.path.isfile("abcd_edit.bvec"):
			print("abcd bval and bvec files have already been copied over for subject " + sub)
			time.sleep(.1)
			os.chdir(rawDir)
			continue
		else:
			print("copying abcd bval and bvec files for subject " + sub)
			shutil.copy("/home/dasay/diffusion/abcd_edit.bval", os.getcwd())
			shutil.copy("/home/dasay/diffusion/abcd_edit.bvec", os.getcwd())
		os.chdir(rawDir)

# creates fieldmaps for each subject


def createFieldmaps(rawDir, subList):
	os.chdir(rawDir)
	for sub in subList:
		os.chdir(sub + niiPath)
		if os.path.isfile("final_fieldmap.nii.gz"):
			print("fieldmap already exists for subject " + sub + "\nmoving to next subject...")
			time.sleep(.1)
			os.chdir(rawDir)
		else:
			print("creating fieldmap for subject " + sub + " ...")
			shutil.copy("/PROJECTS/REHARRIS/explosives/dtiProc/scripts/fslFMAP.sh", os.getcwd())
			os.system("bash fslFMAP.sh")
			os.chdir(rawDir)



def checkOutput(rawDir, subList):
	os.chdir(rawDir)
	badSubs = []
	for sub in subList:
		os.chdir(sub + niiPath)
		if os.path.isfile("final_fieldmap.nii.gz"):
			print("Fieldmap successfully created for subject " + sub)
			time.sleep(.1)
			os.chdir(rawDir)
		else:
			badSubs.append(sub)
			os.chdir(rawDir)
	print("No fieldmaps were created for the following subjects:\n" + str(badSubs) + "\nIf there are no subjects listed, then you're good!")

verifyModules()

subjects = getSubList(rawDir)

changeBVFiles(rawDir, subjects)

createFieldmaps(rawDir, subjects)

checkOutput(rawDir, subjects)
