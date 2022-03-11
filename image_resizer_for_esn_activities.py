# 
# Author: Pavel Kříž
# ESN Section: ISC CTU in Prague
#  
# I took a big part of code from the tutorial for PySimpleGUI at: https://realpython.com/pysimplegui-python/
#
# This app resizes image to 1920x460, maintains aspect ratio and adds white background
# (meets specification of activities.esn.org) 
#

# === APPLICATION LOAD ===

print("Loading application. Wait please...")

# === IMPORTS ===

#from os.path import splitext       
import PySimpleGUI as sg
import os.path
import cv2 as cv
import numpy as np

# === CONSTANTS ===

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

# === RESIZING ===

# function that calculates and returns the resized image
def calc_resized_image(filename):
    # read the image
    in_img = open_image_data(filename)
    # create image of desired size with white background
    out_img = 255 * np.ones((desired_height, desired_width, 3), dtype=np.uint8)

    #get the new size of the content
    scale_factor = min(desired_height / in_img.shape[0], desired_width / in_img.shape[1] )
    content_width = round(in_img.shape[1] * scale_factor)
    content_height = round(in_img.shape[0] * scale_factor)
    
    # scale the content correctly
    out_scaled_img = cv.resize(in_img, (content_width, content_height), interpolation = cv.INTER_AREA)

    # calculate the left corner of the new place for the content
    x_start = round((desired_width - content_width) / 2)
    y_start = round((desired_height - content_height) / 2)

    # put the scaled image into the white image
    out_img[y_start : (y_start + content_height), x_start : (x_start + content_width), 0:3] = out_scaled_img

    # return result
    return out_img


# === LOAD IMAGE ===

# open the image and returning the image data
# opencv does not handle unicode paths, so thats why the open function is used here
def open_image_data(filepath):
    stream = open(filepath, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    # bgr image
    return cv.imdecode(numpyarray, cv.IMREAD_COLOR)


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


# === START INFO ===

print("Ready")

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
            # also encode the image
            if event == "Save jpg":
                out_name = os.path.splitext(filename)[0] + "_ESN_OK" + ".jpg"   
                is_success, im_buf_arr = cv.imencode(".jpg", out_img)
            else:
                out_name = os.path.splitext(filename)[0] + "_ESN_OK" + os.path.splitext(filename)[1]
                is_success, im_buf_arr = cv.imencode(os.path.splitext(filename)[1], out_img)

            # opencv's imwrite does not work with utf8 so the numpy's toFile is used
            im_buf_arr.tofile(out_name)
            # save file
            print("Saved: " + out_name)
        except:
            # file was not probably selected
            pass

# === END ===

# release the window
window.close()