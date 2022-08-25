# ********* This script is to be run AFTER running the preproc03.py script **************
# ********* It will convert freesurfer labels to .mif format and then create a connectome for each subject **************

#### This script has functions that will:
## 1) 
## 2) 
## 3) 
## 4) 

import os
import subprocess
import sys


procDir = "/scratch/seharte_root/seharte99/shared_data/expl/dtiProc"
recon_allDir = "/scratch/seharte_root/seharte99/shared_data/expl/recon-all"


def verifyModules():
	print("Modules loaded:")
	os.system("module list")
	while True:
			loaded = input(f"\n{bcolors.WARNING}For this script, you need the mrtrix and freesurfer modules loaded.\nAre they listed above? If so, type yes and hit enter. \nIf not, please type no and hit enter.\n{bcolors.ENDC}")
			if loaded == "yes" or loaded == "y" or loaded == "Yes" or loaded == "YES":
				print("great! running script...")
				break
			elif loaded == "no" or loaded == "n" or loaded == "No" or loaded == "NO":
				print("\nplease load mrtrix and freesurfer using the following command:\n")
				print("module load mrtrix freesurfer\n")
				print("after loading the module, relaunch the script")
				sys.exit()


def checkIfCompleted(procDir):
	os.chdir(procDir)
	noRunSubList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("sub-CON02_parcels.csv"):
			print("all steps have already been run on subject " + sub)
			noRunSubList.append(sub)
			os.chdir(procDir)
		os.chdir(procDir)
	return noRunSubList

def labelConvert(procDir, noRunList, recon_allDir):
	for sub in getSubListLabelConvert(procDir, noRunList):
		os.chdir(sub)
		print("copying aparc+aseg.mgz file to dtiProc...")
		copyAparc = f"cp {recon_allDir}/{sub}/mri/aparc+aseg.mgz ."
		proc1 = subprocess.Popen(copyAparc, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile(f"aparc+aseg.mgz"):
			print("successfully copied aparc+aseg.mgz for subject " + sub)
		else:
			print("did NOT successfully copy aparc+aseg.mgz for subject " + sub + ". please check")
		print("running labelconvert on subject " + sub + "...")
		labelconvert = f"""
				labelconvert aparc+aseg.mgz $FREESURFER_HOME/FreeSurferColorLUT.txt \
				/sw/arcts/centos7/mrtrix/3.0.3/share/mrtrix3/labelconvert/fs_default.txt \
				{sub}_parcels.mif
				"""
		proc2 = subprocess.Popen(labelconvert, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		if os.path.isfile(f"{sub}_parcels.mif"):
			print("labelconvert ran successfully for subject " + sub)
		else:
			print("labelconvert did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListLabelConvert(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile(f"{sub}_parcels.mif"):
			print("labelconvert has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def tck2Connectome(procDir, noRunList):
	for sub in getSubListTck2Connectome(procDir, noRunList):
		os.chdir(sub)
		print("running tck2connectome on subject " + sub + "...")
		tck2connectome = f"""
					tck2connectome -symmetric -zero_diagonal -scale_invnodevol \
					-tck_weights_in sift_1M.txt tracks_10M.tck \
					{sub}_parcels.mif {sub}_parcels.csv \
					-out_assignment assignments_{sub}_parcels.csv
					"""
		proc1 = subprocess.Popen(tck2connectome, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile(f"{sub}_parcels.csv"):
			print("tck2connectome ran successfully for subject " + sub)
		else:
			print("tck2connectome did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListTck2Connectome(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile(f"{sub}_parcels.csv"):
			print("tck2connectome has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

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


checkIfCompleted(procDir)
verifyModules()
noRunList = checkIfCompleted(procDir)
labelConvert(procDir, noRunList, recon_allDir)
tck2Connectome(procDir, noRunList)

# nodes that do not have any streamlines assigned. may indicate a poor registration:

# 42, 49: reh21exp10016_00235, reh21exp10004_09295, reh21exp10005_09374, reh21exp10023_11058, reh21exp30006_09752, reh21exp10011_00080, reh21exp10006_09459
#cont.		reh21exp10010_10063, reh21exp10024_11082, reh21exp10009_09995, reh21exp30007_09813, reh21exp10015_00266
# 49: reh21exp30006_09842, reh21exp30013_00111
# 42: reh21exp10001_09026, reh21exp10018_00373, reh21exp10017_00388
# 31: reh21exp10021_10880
# 31, 42 : reh21exp10008_10101
# 42, 49, 80: reh21exp30007_09725, reh21exp10007_09429
# 81: reh21exp10002_09153

noProblem = ['reh21exp30013_00281', 'reh21exp30019_00493', 'reh21exp30019_00681', 'reh21exp30020_00875', 'reh21exp30013_00176', 'reh21exp30019_00590', 'reh21exp10020_00568', 'reh21exp30020_00768']

arrayProblem = ['reh21exp10016_00235', 'reh21exp10004_09295', 'reh21exp10005_09374', 'reh21exp10023_11058', 'reh21exp30006_09752', 'reh21exp10011_00080', 'reh21exp10006_09459', 'reh21exp10010_10063', 'reh21exp10024_11082', 'reh21exp10009_09995', 'reh21exp30007_09813', 'reh21exp10015_00266', 'reh21exp30006_09842', 'reh21exp30013_00111', 'reh21exp10001_09026', 'reh21exp10018_00373', 'reh21exp10017_00388', 'reh21exp10021_10880', 'reh21exp10008_10101', 'reh21exp30007_09725', 'reh21exp10007_09429', 'reh21exp10002_09153']

problem = {"42, 49": ["reh21exp10016_00235", "reh21exp10004_09295", "reh21exp10005_09374", "reh21exp10023_11058", "reh21exp30006_09752", "reh21exp10011_00080", "reh21exp10006_09459", "reh21exp10010_10063", "reh21exp10024_11082", "reh21exp10009_09995", "reh21exp30007_09813", "reh21exp10015_00266"],			
"49": ["reh21exp30006_09842", "reh21exp30013_00111"], "42": ["reh21exp10001_09026", "reh21exp10018_00373", "reh21exp10017_00388"], 
"31": ["reh21exp10021_10880"], "31, 42": ["reh21exp10008_10101"], "42, 49, 80": ["reh21exp30007_09725", "reh21exp10007_09429"],
"81": ["reh21exp10002_09153"]}


