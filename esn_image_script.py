# 
# Author: Pavel Kříž
# ESN Section: ISC CTU in Prague
#  
# I took a big part of code from the tutorial for PySimpleGUI at: https://realpython.com/pysimplegui-python/
#
# This app resizes image to 1920x460, maintains aspect ratio and adds white background
# (meets specification of activities.esn.org) 
#

#from os.path import splitext       
import PySimpleGUI as sg
import os.path
import cv2 as cv
import numpy as np

# 1920 (width) x 460 (height) is the ESN form format
desired_width = 1920
desired_height = 460


# file formats that are supported
supported_extensions = (".bmp",
                            ".dib",
                            ".jpeg",
                            ".jpg",
                            ".png",
                            ".webp",
                            ".pbm",
                            ".pgm",
                            ".ppm",
                            ".pxm",
                            ".pnm",
                            ".tiff",
                            ".tif",
                            ".hdr",)


# when the image has tighter angle than the ESN specification 
# out_image should be image of size 1920x460 with 255 value everywhere
def scale_to_match_height(in_img, out_img):
    # get sizes
    content_width = round(in_img.shape[1] * (desired_height / in_img.shape[0]))
    content_height = desired_height

    # scale the content correctly
    out_scaled_img = cv.resize(in_img, (content_width, content_height), interpolation = cv.INTER_AREA)

    # put the scaled image into the white image
    x_start = int(desired_width / 2 - content_width / 2)
    out_img[0: content_height, x_start : (x_start + content_width), 0:3] = out_scaled_img


# when the image has wider angle than the ESN specification 
# out_image should be image of size 1920x460 with 255 value everywhere
def scale_to_match_width(in_img, out_img):
    # get sizes
    content_width = desired_width
    content_height = round(in_img.shape[0] * (desired_width / in_img.shape[1]))

    # scale the content correctly
    out_scaled_img = cv.resize(in_img, (content_width, content_height), interpolation = cv.INTER_AREA)

    # put the scaled image into the white image
    y_start = int(desired_height / 2 - content_height / 2)
    out_img[y_start : (y_start + content_height),0 : content_width, 0:3] = out_scaled_img


# function that calculates and returns the resized image
def calc_resized_image(filename):
    # read the image
    in_img = cv.imread(filename, cv.IMREAD_COLOR)
    out_img = 255 * np.ones((desired_height, desired_width, 3), dtype=np.uint8)

    # decide if the image has less wider angle then the ESN specification 
    if in_img.shape[1] / in_img.shape[0] < desired_width / desired_height:
        # it does not have wider angle
        scale_to_match_height(in_img, out_img)
    else:
        # it has wider angle
        scale_to_match_width(in_img, out_img)

    return out_img


# === LAYOUT ===
# layout is divided in two main parts, left and right one
# left column/part
file_list_column = [
    [
        sg.Text("Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]
# right column/part
image_viewer_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(100, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
    [sg.Button("Save jpg"), sg.Button("Save")],
]
# merging column layouts together
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

# === APPLICATION LOOP ===
# create window
window = sg.Window("Image resizer for activities.esn.org", layout)
# run the application loop
while True:
    event, values = window.read()
    # catch events
    if event == "Exit" or event == sg.WIN_CLOSED:
        # breaking the application loop
        break

    # Folder name was filled in, make a list of files in the folder
    elif event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            # empty list instead
            file_list = []
        # filter the names in the list just to supported images    
        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith(supported_extensions)
        ]
        # update the list in the window
        window["-FILE LIST-"].update(fnames)
    # A file/image was chosen from the listbox
    elif event == "-FILE LIST-":
        try:
            # get the filepath to the image
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update("Preview of: " + filename)

            # calculate the image
            out_img = calc_resized_image(filename)
            
            # create preview (here it is not an optimization, just making the image smaller)
            preview_width = int(desired_width / 3)
            preview_height = int(desired_height / 3)
            preview = cv.resize(out_img, (preview_width, preview_height), interpolation = cv.INTER_AREA)
            # the pysimple gui needs the image as png - so the image is encoded as png 
            # then stored in binray and fed to the pysimplegui
            img_bytes = cv.imencode('.png', preview)[1].tobytes()
            #show preview
            window["-IMAGE-"].update(data=img_bytes)
        except:
            pass
    # does user want to save the image? - checking the buttons
    elif event == "Save" or event == "Save jpg":
        try:
            # get the filepath to the image
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )

            # calculate the image
            out_img = calc_resized_image(filename)

            # does the user wants to save it in original format or jpg?
            if event == "Save jpg":
                out_name = os.path.splitext(filename)[0] + "_ESN_OK" + ".jpg"   
            else:
                out_name = os.path.splitext(filename)[0] + "_ESN_OK" + os.path.splitext(filename)[1]
            # save file
            cv.imwrite(out_name, out_img)
        except:
            # file was not probably selected
            pass

# release the window
window.close()