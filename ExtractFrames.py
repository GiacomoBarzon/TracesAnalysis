import os

envi = os.environ['HOME']

#force input framerate to convert h264 into mp4
h264framerate=25	#fps
#force framestep to create frames from mp4
framestep=5

#VIDEO CONVERSION FROM.H264 FORMAT TO .MP4
#input: h264 video folder, mp4 video folder
def converti(path_h264, path_mp4):
    print('Start conversion\n')
    if not (os.path.exists(path_h264) or os.path.exists(path_mp4)):
        return
    for filename in os.listdir(path_h264):
        #read h264 files
        if (filename.endswith(".h264")):
            print('found '+filename )
            name, dot, extension=filename.partition('.')
            #create mp4 from h264 with a specified frame rate
            os.system("ffmpeg -framerate "+str(h264framerate)+" -i {0} -c copy {1}.mp4".format(path_h264+filename, path_mp4+name))
        else:
            continue
    print('End conversion\n')

#VIDEO SEGMENTATION IN 15 SECONDS PARTS
def segmenta(path_to_segment, path_mp4):
    print('Start segmentation\n')
    if not (os.path.exists(path_to_segment) or os.path.exists(path_mp4)):
        return
    for filename in os.listdir(path_to_segment):
        if (filename.endswith(".mp4")):
            print('found '+filename )
            name, dot, extension=filename.partition('.')
            #Video segmentation in 15 seconds parts
            os.system("ffmpeg -i {1}{0}.mp4 -c copy -f segment -segment_time 15 -reset_timestamps 1 {2}seg%d_{0}.mp4".format(name, path_to_segment, path_mp4))
        else:
            continue
    print('End segmentation\n')

#CUT VIDEO IN FRAMES
#input: mp4 video folder, output folder
def taglia(path_mp4, path_frames):
    print('Start extracting frames\n')
    if not (os.path.exists(path_frames) or os.path.exists(path_mp4)):
        return
    for filename in os.listdir(path_mp4):
        if (filename.endswith(".mp4")):
            print('found '+filename )
            name, dot, extension=filename.partition('.')
            #segmenta il video in parti di circa 15 secondi
            os.system("ffmpeg -i {1}{0} -vf 'tblend=addition,framestep={2}'".format(filename, path_mp4,framestep)+" {2}{0}-%d.png".format(name, path_mp4, path_frames))
        else:
            continue
    print('\nEnd extracting frames\n')

#CUT SINGLE VIDEO IN FRAMES
#input: mp4 video folder, video name, output folder
def cutVideo(path_mp4, filename, path_frames):
    print('Start cutting video ')
    if not(os.path.exists(path_mp4)):
        print('La directory dei video .mp4 non esiste oppure e sbagliata\n')
        return
    name, dot, extension=filename.partition('.')
    os.system("ffmpeg -i {1}{0} -vf 'tblend=addition,framestep={2}'".format(filename, path_mp4,framestep)+" {2}{0}-%d.png".format(name, path_mp4, path_frames))

