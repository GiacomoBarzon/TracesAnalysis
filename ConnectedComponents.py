import numpy as np
from PIL import Image
import os
import math
import cv2
import time
import matplotlib as mpl
mpl.use('Agg')
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from matplotlib import pyplot as plt
import scipy
from scipy import ndimage

import Filters
import TriggerFunctions
import shutil

from tqdm import tqdm

#PARAMETERS FOR FILTERS
#this value should be adapted to the experimental setup
denoising1_bkg=5
dilation_bkg=6
denoising1=8
denoising2=0.80
denoising2_sub=0.0078
max_pool=2

gauss_radius_1 = 2.3
loCcThr_1 = 4000
hiCcThr_1 = 100000

gauss_radius_2 = 1.5
loCcThr_2 = 4000
hiCcThr_2 = 300000

discriminant_thr=0.004

#VIDEO ANALYSIS: Extract traces from frames
#input: outputpath, video name, folder with frames, folder to save traces
#       path for logbook, folder to save mean and variance matrix
def VideoAnalysis(path_out, video_name,
                  frames_folder, traces_folder, log_path, stat_path):
        print('STARTING VIDEO ANALYSIS:\n')

        #temporary folder to save filtered image before labeling
        output_folder_mean = path_out+'toLabel/'
        output_folder = path_out+'pooled/'

        if not os.path.exists(output_folder_mean):
                os.makedirs(output_folder_mean)
        if not os.path.exists(output_folder):
                os.makedirs(output_folder)

        #setup parameters
        signals = 0
        total_traces=0
        start = time.time()

        n_frames = TriggerFunctions.TotalFrames(frames_folder)
        image_prototype=Image.open(str(frames_folder)+video_name+'-1.png')
        matrix_prototype=np.asarray(image_prototype.convert('L'))
        print("Number of frames: "+str(n_frames)+'\n')
        log_text=open(log_path, "a")
        log_text.write("Number of frames analyzed: "+str(n_frames)+'\n')
        log_text.close()
        
        #Normalized mean and variance matrices
        matrix_mean, matrix_var = TriggerFunctions.TotalMeanVar(frames_folder, matrix_prototype, n_frames)

        #Saving mean and variance matrices
        plt.matshow(matrix_var)
        plt.colorbar()
        plt.savefig(str(stat_path)+'var_'+str(video_name)+'.png')

        plt.matshow(matrix_mean)
        plt.colorbar()
        plt.savefig(str(stat_path)+'mean_'+str(video_name)+'.png')

        #LOOP ON FRAMES
        for file_raw in tqdm(os.listdir(frames_folder)):
                if not file_raw.endswith('.png'):
                        continue
                if (file_raw.endswith('-1.png') or file_raw.endswith('-2.png')
                    or file_raw.endswith('-3.png') or file_raw.endswith('-4.png')):
                        continue
                raw_image = Image.open(str(frames_folder)+file_raw)
                matrix_raw=np.asarray(raw_image.convert('L'))
                
                #Selecting relevant frames via discriminant value
                if not TriggerFunctions.ImageSelectingByDiscrimination(matrix_raw/255., matrix_mean, matrix_var, discriminant_thr, verbose = True):
                        continue
                               
                signals+=1
                log_text=open(log_path, "a")
                log_text.write('\nSelected file number '+str(signals)+': '+str(file_raw)+'\n')
                log_text.close()
                print('\nSelected file number '+str(signals)+': '+str(file_raw)+'\n')

                raw_file_name, dot, formato = file_raw.partition('.')
                temp_file_name = raw_file_name.split('-')
                number_frame=int(temp_file_name[-1])

                Filters.ReducingResolution(frames_folder, file_raw, output_folder, 'raw_pooled.png', max_pool)
                raw_pooled = Image.open(str(output_folder)+'raw_pooled.png')
                matrix_raw_pooled=np.asarray(raw_pooled.convert('L'))
                matrix_mean_pooled = np.zeros_like(matrix_raw_pooled)
                
                #SUBTRACTING BACKGROUNDS PROCEDURE
                #counting the number of background frames
                n_backgrounds=0
                start_partial=time.time()
                for file in os.listdir(frames_folder):
                        if (file.startswith(video_name)):
                                if (file.endswith('-1.png') or file.endswith('-2.png') 
                                    or file.endswith('-3.png') or file.endswith('-4.png') 
                                    or file == file_raw):
                                        continue
                                file_name, dot, extension = file.partition('.')
                                file_name1 = file_name.split('-')
                                number=int(file_name1[-1])
                                if (number%3):
                                        continue
                                n_backgrounds += 1
                log_text=open(log_path, "a")
                log_text.write('Total number of background images processed: '+str(n_backgrounds)+'\n')
                log_text.close()
                print('Total number of background images processed: '+str(n_backgrounds)+'\n')

                for file in os.listdir(frames_folder):
                        if (file.startswith(video_name)):
                                if (file.endswith('-1.png') or file.endswith('-2.png') 
                                    or file.endswith('-3.png') or file.endswith('-4.png')
                                    or file == file_raw):
                                        continue
                                file_name, dot, extension = file.partition('.')
                                file_name1 = file_name.split('-')
                                number=int(file_name1[-1])
                                if (number%3):
                                        continue
                                #background manipulation before subtracting
                                Filters.Denoising1(frames_folder, file, output_folder, 'bkg_denoising1.png', denoising1_bkg)
                                Filters.Dilation(output_folder, 'bkg_denoising1.png', output_folder, 'bkg_dilationed.png', dilation_bkg)
                                #raw_image manipulation before subtracting
                                Filters.Denoising1(frames_folder, file_raw, output_folder, 'raw_denoising1.png', denoising1)
                                #background subtraction
                                Filters.BackgroundSubtraction(output_folder, 'raw_denoising1.png', 'bkg_dilationed.png', output_folder, 'subtracted.png')
                                #manipulation after subtracting
                                Filters.Denoising2(output_folder, 'subtracted.png', output_folder, 'sub_denoising2.png', denoising2_sub)
                                Filters.ReducingResolution(output_folder, 'sub_denoising2.png', output_folder, 'pool_'+str(file), max_pool)
                                image_pooled = Image.open(str(output_folder)+'pool_'+str(file))
                                matrix_pooled=np.asarray(image_pooled.convert('L'))
                                matrix_mean_pooled=np.add(matrix_mean_pooled*1., matrix_pooled*1./n_backgrounds)

                #meaning subtracted images
                image_mean = Image.fromarray(np.uint8(matrix_mean_pooled))
                image_mean.save(str(output_folder_mean)+'mean_'+str(raw_file_name)+'.png')
                #binarization
                Filters.Denoising2(output_folder_mean, 'mean_'+str(raw_file_name)+'.png', output_folder_mean, 'mean_'+str(raw_file_name)+'_den2.png', denoising2)
                
                #LABELING
                temp_folder_1 = path_out+'temp1/'
                temp_folder_2 = path_out+'temp2/'
                if os.path.exists(temp_folder_1):
                        shutil.rmtree(temp_folder_1)
                if os.path.exists(temp_folder_2):
                        shutil.rmtree(temp_folder_2)
                os.makedirs(temp_folder_1)
                os.makedirs(temp_folder_2)
                
                #first labeling
                n1=Filters.HiLoLabeling(output_folder_mean, 'mean_'+str(raw_file_name)+'_den2.png', traces_folder, temp_folder_1,
                                     gauss_radius_1, loCcThr_1, hiCcThr_1)
                #second labeling
                n2=0
                for temp_cc in os.listdir(temp_folder_1): 
                       q=Filters.HiLoLabeling(temp_folder_1, temp_cc, traces_folder, temp_folder_2,
                                             gauss_radius_2, loCcThr_2, hiCcThr_2)
                       n2+=q
                #deleting temporary folders
                shutil.rmtree(temp_folder_1)
                shutil.rmtree(temp_folder_2)

                total_cc=n1+n2 #+n3
                total_traces+=total_cc
                log_text=open(log_path, "a")
                '''
                log_text.write("Number of traces finded: "+str(total_cc)+'\n')
                log_text.write("Time required for one frame to be analyzed: "+str(delta_partial)+' sec \n'+
                               "Integrated time from the beginning: "+str(delta_integrated)+' sec \n')
                log_text.close()
                print("Number of traces finded: "+str(total_cc)+'\n')
                print("Time required for one frame to be analyzed: "+str(delta_partial)+' sec \n'+
                               "Integrated time from the beginning: "+str(delta_integrated)+' sec \n')
                '''
        stop=time.time()
        delta=stop-start
        log_text=open(log_path, "a")
        log_text.write("\nTotal time for the execution: "+str(delta)+' sec\n\n'+
                       "Total number of frames selected for the analysis: "+str(signals)+'\n')
        log_text.write("Total traces:"+str(total_traces)+str('\n\n\n'))
        log_text.close()
        print("Total time for the execution: "+str(delta)+' sec \n\n'+
                       "Total number of frames selected for the analysis: "+str(signals)+'\n')
        print("Total traces:"+str(total_traces)+str('\n\n\n'))

        #deleting temporary folders
        shutil.rmtree(output_folder_mean)
        shutil.rmtree(output_folder)


