import torch
import os
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime
import matplotlib.pyplot as plt
import random


# These are the objects to be identified and counted in a give image
OBJ_TYPES_TO_COUNT = ['bicycle', 'car', 'motorcycle', 'bus', 'truck', 'person']
torch.cuda.is_available = lambda: False

def unique(list1):
    """ Method to get unique values in a list"""
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    return list(list_set)


def list_jpgs(tmp_dir):
    """ List all jpg files in a directory """
    jpg_paths = []
    # Local directory for storing test images
    for (dirpath, dirnames, filenames) in os.walk(tmp_dir):
        for filename in filenames:
            if '.jpg' in filename:
                jpg_paths.append(os.path.join(dirpath, filename))
    return jpg_paths


class PlotSingleImage:
    """ Plot a Single Image Showing the Results from YoloV5 and a Timestamp """
    def __init__(self, dir):
        self.dir = dir

        img_paths = list()
        for (dirpath, dirnames, filenames) in os.walk(self.dir):
            if 'SaveImageResults' in dirpath:
                img_paths.append(dirpath)

        # Plot YoloV5 results images into a single image for viewing
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        plt.tight_layout()
        img = np.asarray(Image.open(img_paths[random.randint(0, 1)] + '/image0.jpg'))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Updated On: " + datetime.now().strftime("%B %d, %Y %H:%M:%S"))
        ax.imshow(img)
        plt.tight_layout()
        fig.savefig(self.dir + 'Single_Image.jpg')


def count_vehicles(model, img_path):
    """ Count the number of objects in an image """
    # Load image from disk into numpy array
    img = np.asarray(Image.open(img_path))

    # YoloV5 results for a single image
    results = model(img)

    # Loop over the prediction for a given image and extract the count for each object type identified
    obj_ints = [int(results.pred[0][j][5]) for j in range(results.pred[0].shape[0])]
    obj_names = [results.names[i] for i in obj_ints]

    # Store the counts for each object type in a dictionary
    obj_counts = {}
    for obj_type_to_count in OBJ_TYPES_TO_COUNT:
        obj_counts[obj_type_to_count] = obj_names.count(obj_type_to_count)
    return obj_counts, results


def obj_det_update(tmp_dir, df_disk, s3_data):
    """ Execute the YoloV5 model to find objects in each web scrapped image from EarthCam """
    # Load YoloV5 Model using Torch Hub
    if 'home' in os.getcwd():
        repo_or_dir = './yolov5'  # Local syntax for development
    else:
        repo_or_dir = '/var/task/yolov5'  # AWS Lambda syntax for Docker Container
    model = torch.hub.load(repo_or_dir,
                           'custom',
                           path='yolov5n.pt',
                           source='local',
                           )
    model.conf = 0.25  # NMS confidence threshold

    # Get datetimes from images on disk
    img_paths = list_jpgs(tmp_dir=tmp_dir)
    unique_dates = unique([i.split('/')[-1].split('__')[0].split(' ')[0] for i in img_paths])
    unique_dates = sorted(unique_dates)

    # Remove images if they are not a day old because there are likely more images and it will skew the results
    current_datetime = datetime.now().strftime("%d-%b-%Y")
    if current_datetime in unique_dates:
        unique_dates.remove(current_datetime)

    # Create an empty dataframe for storing results
    df = pd.DataFrame(columns=['date'] + OBJ_TYPES_TO_COUNT)
    df['date'] = unique_dates
    df.fillna(0, inplace=True)

    # Count Objects in Images saved on disk
    for i, img_path in enumerate(img_paths):
        objs, model_results = count_vehicles(model=model, img_path=img_path)
        date = img_path.split('/')[-1].split('__')[0].split(' ')[0]
        img_name = img_path.split('/')[-1].split('__')[1]
        if date in unique_dates:
            row_idx = df.index[df['date'] == date].tolist()[0]
            for obj_type in OBJ_TYPES_TO_COUNT:
                count = df.at[row_idx, obj_type] + objs[obj_type]
                df.loc[row_idx, obj_type] = count

            if i > len(img_paths) - 4:
                results_save_path = tmp_dir + 'SaveImageResults_' + img_name[:-4]
                model_results.save(save_dir=results_save_path)

    # Plot individual model results into a single image and remove result images from disk
    if len(img_paths) != 0:
        PlotSingleImage(dir=tmp_dir)

    # Check for duplicates dates and only store new information
    if df.empty:
        df_updated = df_disk
    else:
        df_updated = df_disk.append(df)
        df_updated.drop_duplicates(subset=['date'], keep='last', inplace=True)
        df_updated.sort_values('date', key=pd.to_datetime, inplace=True)

    # Delete all downloaded images in tmp folder
    temp_imgs_dir = tmp_dir
    for f in os.listdir(temp_imgs_dir):
        if ("__" in f) and ('.jpg' in f):
            os.remove(temp_imgs_dir + f)
            print(f'Deleted {temp_imgs_dir + f}')

    print('Finished Object Detection')
    return df_updated

