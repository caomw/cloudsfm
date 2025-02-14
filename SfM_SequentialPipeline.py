#!/usr/bin/python
#! -*- encoding: utf-8 -*-

# Python implementation of the bash script written by Romuald Perrot
# Created by @vins31
# Modified by Pierre Moulon and Dany Laksono
# 
# this script is for easy use of OpenMVG
#
# usage : python openmvg.py image_dir output_dir 
#
# image_dir is the input directory where images are located 
# output_dir is where the project must be saved
# 
# if output_dir is not present script will create it 
# 

# Indicate the openMVG binary directory
OPENMVG_SFM_BIN = "/home/dany/github/openMVG_Build/software/SfM"

# Indicate the openMVG camera sensor width directory
CAMERA_SENSOR_WIDTH_DIRECTORY = "/home/dany/github/openMVG/src/software/SfM" + "/cameraSensorWidth"

import commands
import os
import subprocess
import sys, getopt

if len(sys.argv) < 3:
    print ("Usage %s image_dir output_dir" % sys.argv[0])
    sys.exit(1)
    
input_dir = ''
output_dir = ''
cam_focus = ''


try:
  opts, args = getopt.getopt(sys.argv[1:],"hi:o:f:",["input=","output=", "focus=" ])
except getopt.GetoptError:
  print 'test.py -i <inputfile> -o <outputfile> -f <focuslength>'
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
	 print 'test.py -i <inputfile> -o <outputfile>'
	 sys.exit()
  elif opt in ("-i", "--input"):
	 input_dir = arg
  elif opt in ("-o", "--output"):
	 output_dir = arg
  elif opt in ("-f", "--focus"):
	 cam_focus = arg

#input_dir = sys.argv[1]
#output_dir = sys.argv[2]

matches_dir = os.path.join(output_dir, "matches")
reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")
camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "cameraGenerated.txt")

print ("Using input dir 		: ", input_dir)
print ("      output_dir 		: ", output_dir)
print ("Estimated camera focus 	: ", cam_focus)

# Create the ouput/matches folder if not present
if not os.path.exists(output_dir):
  os.mkdir(output_dir, 0755)
if not os.path.exists(matches_dir):
  os.mkdir(matches_dir, 0755)

print ("1. Intrisics analysis") 
# modified to include camera with unknown parameter
if cam_focus != '':
	print ("Camera model or intrinsic parameter unknown. Using estimated focus")
	pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-f", cam_focus])
	pIntrisics.wait()
else:
	pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params] )
	pIntrisics.wait()

print ("2. Compute features")
pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT"] )
pFeatures.wait()

print ("3. Compute matches")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-r", "0.8"] )
pMatches.wait()

# Create the reconstruction if not present
if not os.path.exists(reconstruction_dir):
    os.mkdir(reconstruction_dir, 0755)

print ("4. Do Global reconstruction")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
pRecons.wait()

print ("5. Colorize Structure")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.json", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pRecons.wait()

# optional, compute final valid structure from the known camera poses
print ("6. Structure from Known Poses (robust triangulation)")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.json", "-m", matches_dir, "-f", os.path.join(matches_dir, "matches.f.txt"), "-o", os.path.join(reconstruction_dir,"robust.json")] )
pRecons.wait()

pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/robust.json", "-o", os.path.join(reconstruction_dir,"robust_colorized.ply")] )
pRecons.wait()


