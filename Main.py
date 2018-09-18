import ExtractFrames
import ConnectedComponents as CC
import CenterTraces as CT

import shutil
import math
import sys

import os

endLine = '\n'

#FINAL ALGORITHM
#for each video, the actions are:
#1) frames extraction
#2) frames analysis-> foreground removal,Connected Components search
#3) rotation and centering

print('FINAL ALGORITHM FOR TRACES SEARCH\n')

final_dimension = 128 # dimension of analyzed images

#before running the code export DATA_PATH where background and raw files are placed (date)
envi = os.environ['HOME']

'''
    REPLACE WITH YOUR OWN DIRECTORIES
'''
#input path
path = '/Users/handing/Desktop/piVideo/' #principal directory path
path_h264 = path + 'videoOk/video_h264/'
#output path
path_mp4 = path + 'videoOk/video_mp4/'
path_out = path + 'databaseFinale/'
path_cc = path_out + 'cc/'
path_stat = path_out + 'stat/'
path_traces = path_out + 'traces/'

if not os.path.exists(path_h264):
    print('Directory containing videos doesn t exist\n')
    sys.exit()

#output directory creation
if not os.path.exists(path_mp4):
    os.makedirs(path_mp4)
if not os.path.exists(path_out):
    os.makedirs(path_out)
if not os.path.exists(path_cc):
    os.makedirs(path_cc)
if not os.path.exists(path_stat):
    os.makedirs(path_stat)

#log file .txt creation
log_path = path_out + 'log_book.txt'

#VIDEO CONVERSION
path_temp_mp4 = path_out + 'videoOk/temp_video_mp4/'
if not os.path.exists(path_temp_mp4):
    os.makedirs(path_temp_mp4)
    
ExtractFrames.converti(path_h264, path_temp_mp4)
ExtractFrames.segmenta(path_temp_mp4, path_mp4)

if os.path.exists(path_temp_mp4):
        shutil.rmtree(path_temp_mp4)


#compute total video time
total_video=0
for video in os.listdir(path_mp4):
    if not (video.endswith('.mp4')):
        continue
    total_video += 1
secondi_totali=total_video*15 #estimation of complete video time in seconds
minuti_totali=secondi_totali/60. #estimation of complete video time in minutes

print('Total number of video: '+str(total_video)+str(endLine))
log_text=open(log_path, "w")
log_text.write('********AUTOMATIC ANALYSIS OF CLOUD CHAMBER IMAGES********'+str(endLine)+str(endLine))
log_text.write('Total number of video: '+str(total_video)+str(endLine))
log_text.write('Complete video time: '+str(math.fabs(minuti_totali))+'minutes\n\n')
log_text.close()

#LOOP ON VIDEO
number_video=0
for video in os.listdir(path_mp4):
    if not (video.endswith('.mp4')):
        continue
    number_video += 1
    print('******VIDEO ANALYSIS '+str(number_video)+'/'+str(total_video)+str('******')+str(endLine))
    print('***video name: '+str(video)+'***\n\n')
    log_text=open(log_path, "a")
    log_text.write('******VIDEO ANALYSIS '+str(number_video)+'/'+str(total_video)+str('******')+str(endLine))
    log_text.write('***video name: '+str(video)+'***\n\n')
    log_text.close()

    #FRAMES EXTRACTION
    #creation of temporary frames folder
    path_temp_frames = path_out + 'temp_frames/'
    if os.path.exists(path_temp_frames):
        shutil.rmtree(path_temp_frames)
    os.makedirs(path_temp_frames)
    #frames extraction from file .mp4
    ExtractFrames.cutVideo(path_mp4, video, path_temp_frames)

    #FRAMES ANALYSIS-CONNECTED COMPONENTS SEARCH
    video_name, dot, formato = video.partition('.')
    CC.VideoAnalysis(path_out, video_name, path_temp_frames, path_cc, log_path, path_stat)

#CENTERING AND ROTATION TRACES
for frame in os.listdir(path_cc):
    if not (video.endswith('.png')):
        continue
    CT.refine_image(path_cc, frame, path_traces, final_dimension)

if os.path.exists(path_cc):
        shutil.rmtree(path_cc)
