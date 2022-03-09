from os.path import splitext
import PySimpleGUI as sg
import os.path
import cv2 as cv
import numpy as np

# 1920 x 460 
desired_width = 1920
desired_height = 460

def scale_to_match_height(in_img, out_img):
    content_width = round(in_img.shape[1] * (desired_height / in_img.shape[0]))
    content_height = desired_height

    out_scaled_img = cv.resize(in_img, (content_width, content_height), interpolation = cv.INTER_AREA)

    # put the scaled image into the zero ones
    x_start = int(desired_width / 2 - content_width / 2)

    out_img[0: content_height, x_start : (x_start + content_width), 0:3] = out_scaled_img


def scale_to_match_width(in_img, out_img):
    content_width = desired_width
    content_height = round(in_img.shape[0] * (desired_width / in_img.shape[1]))

    out_scaled_img = cv.resize(in_img, (content_width, content_height), interpolation = cv.INTER_AREA)
    # put the scaled image into the zero ones
    y_start = int(desired_height / 2 - content_height / 2)

    out_img[y_start : (y_start + content_height),0 : content_width, 0:3] = out_scaled_img


def calc_resized_image(filename):
    in_img = cv.imread(filename)
    out_img = 255 * np.ones((desired_height, desired_width, 3), dtype=np.uint8)

    # normal
    if in_img.shape[1] / in_img.shape[0] < desired_width / desired_height:
        scale_to_match_height(in_img, out_img)
    # even more wide
    else:
        scale_to_match_width(in_img, out_img)

    return out_img


# First the window layout in 2 columns
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

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
    [sg.Button("Save")],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Image Viewer", layout)
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder

    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []
        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".gif", ".jpg"))
        ]
        window["-FILE LIST-"].update(fnames)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)

            out_img = calc_resized_image(filename)
            
            #create preview
            preview_width = int(desired_width / 3)
            preview_height = int(desired_height / 3)
            preview = cv.resize(out_img, (preview_width, preview_height), interpolation = cv.INTER_AREA)
            img_bytes = cv.imencode('.png', preview)[1].tobytes()  # ditto
            #show preview
            window["-IMAGE-"].update(data=img_bytes)
        except:
            pass

    if event == "Save": #user wants to save the image
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            
            out_img = calc_resized_image(filename)

            out_name = splitext(filename)[0] + "_ESN_OK" + splitext(filename)[1]
            cv.imwrite(out_name, out_img)
        except:
            pass

window.close()