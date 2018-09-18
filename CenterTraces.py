import numpy as np
from PIL import Image
import os
import math
import cv2
import scipy
from scipy import ndimage

#PAD IMAGE: Add padding of zeroes to an image
#input: image, pad top, pad right, pad bottom, pad left
def pad_image(img, pad_t, pad_r, pad_b, pad_l):
    
    height, width = img.shape

    # Adding padding to the left side.
    pad_left = np.zeros((height, pad_l), dtype = np.int)
    img = np.concatenate((pad_left, img), axis = 1)

    # Adding padding to the top.
    pad_up = np.zeros((pad_t, pad_l + width))
    img = np.concatenate((pad_up, img), axis = 0)

    # Adding padding to the right.
    pad_right = np.zeros((height + pad_t, pad_r))
    img = np.concatenate((img, pad_right), axis = 1)

    # Adding padding to the bottom
    pad_bottom = np.zeros((pad_b, pad_l + width + pad_r))
    img = np.concatenate((img, pad_bottom), axis = 0)

    return img

#CENTER IMAGE: Return a centered image
#input: image
def center_image(img):
    
    #Find non-zero rows and columns
    col_sum = np.where(np.sum(img, axis=0) > 0)
    row_sum = np.where(np.sum(img, axis=1) > 0)
    y1, y2 = row_sum[0][0], row_sum[0][-1]
    x1, x2 = col_sum[0][0], col_sum[0][-1]
    
    #Select region of interest
    cropped_image = img[y1:y2, x1:x2]

    #Add padding
    zero_axis_fill = (img.shape[0] - cropped_image.shape[0])
    one_axis_fill = (img.shape[1] - cropped_image.shape[1])

    top = zero_axis_fill / 2
    bottom = zero_axis_fill - top
    left = one_axis_fill / 2
    right = one_axis_fill - left

    padded_image = pad_image(cropped_image, top, left, bottom, right)

    return padded_image

#ROTATE IMAGE: Return a rotated image
#input: image
def rotate_image(img):

    #Find contours
    i, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #Join contours and find min Area Rect
    if len(contours) > 1:
        temp = np.concatenate(contours)
        center, sides, angle = cv2.minAreaRect(temp)#side0: height, side1: width
    if len(contours) == 1:
        center, sides, angle = cv2.minAreaRect(contours)

    #Get the rect's angle of rotation    
    if(sides[1] < sides[0]):
        angle = angle -90

    #Rotate image
    angleOk=angle+90
    rotated_image = ndimage.rotate(img, angleOk)

    return rotated_image

#CUT IMAGE: Return an image with the initial shape, cause the modified image as bigger shape
#input: image, output height, output width
def cut_image(img, out_height, out_width):
    
    #Center of the modified image
    center_x = img.shape[1]/2
    center_y = img.shape[0]/2

    #Define output dimension
    x1 = center_x - out_width/2
    x2 = center_x + out_width/2
    y1 = center_y - out_height/2
    y2 = center_y + out_height/2

    cut_image = img[y1:y2, x1:x2]

    return cut_image


#REFINE IMAGE: Rotate with adding padding, center, cutted and resize image
#input: inputpath, image, outputpath, output shape (square)
def refine_image(inputpath, inputfile, outputpath, out_shape):
    
    image_in = cv2.imread(str(inputpath)+inputfile,0)
    #original image shape: 540 x 960
    
    image_rotated = rotate_image(image_in)
    image_centered = center_image(image_rotated)
    image_cutted = cut_image(image_centered, image_in.shape[0], image_in.shape[0])
    #temp_shape: 540 x 540
    image_resize = cv2.resize(image_cutted, (out_shape, out_shape), interpolation = cv2.INTER_AREA)
    cv2.imwrite(str(outputpath)+'ok-'+str(inputfile), image_resize)
