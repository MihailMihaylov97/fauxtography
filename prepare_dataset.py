from __future__ import annotations
from turtle import done
import requests
import argparse
import json
from glob import glob
from tqdm import tqdm
import re
import numpy as np

def download(data_path, annotations_info):   
    img_data = requests.get(annotations_info["image"]["url"]).content
    with open(f'{data_path}/images/{annotations_info["image"]["filename"]}', 'wb') as handler:
        handler.write(img_data)

def calculate_polygon_area(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--data_path', help='Provide the path to the folder with data', required=True)
    parser.add_argument('--download_data', help='Whether to download the data or not', default=False, action='store_true')
    parser.add_argument('--annotation_name', help='Provide annotations json name', required=True)
    args = parser.parse_args()

    download_data = args.download_data

    annotations = glob(f"{args.data_path}/*.json")
    unique_categories, annotation_id = [], 0
    annotations_coco = {"categories":[], "images":[], "annotations":[]}
    
    if download_data:
        from pathlib import Path
        Path(f"{args.data_path}/images").mkdir(parents=True, exist_ok=True)
                

    for id, annotation in tqdm(enumerate(annotations)):

        try:
            with open(annotation) as annotation_file:
                annotations_info = json.load(annotation_file)

                if download_data:
                    download(args.data_path, annotations_info)
                    
                annotations_coco["images"].append({"id":id,
                                         "file_name":annotations_info["image"]["filename"],
                                         "height":annotations_info["image"]["height"],
                                         "width":annotations_info["image"]["width"],
                                         })

                if len(annotations_info["annotations"])>5: print(annotations_info)
                for annot in annotations_info["annotations"]:
                    if "polygon" in annot:
                        if annot["name"] not in unique_categories:
                            unique_categories.append(annot["name"])

                        float_numbers = re.findall("\d+\.\d+", str(annot["polygon"]["path"]))
                        segmentation_points = [float(i) for i in float_numbers]
                        x_s = segmentation_points[0::2]
                        y_s = segmentation_points[1::2]
                        bbox = [max(x_s), max(y_s), min(x_s), min(y_s)]
                        annotations_coco["annotations"].append({"id": annotation_id,
                                                "image_id":id,
                                                "category_id":unique_categories.index(annot["name"]),
                                                "segmentation":segmentation_points,
                                                "bbox":bbox,
                                                "area":calculate_polygon_area(segmentation_points[0::2],segmentation_points[1::2])
                                                })
                        annotation_id += 1
                        
        except Exception as e:
            print(annotation)
            print(e)
            # break
    

    for i, category in enumerate(unique_categories):
        annotations_coco["categories"].append({"id":i,
                                               "name":category,
                                               "supercategory":"parrot"})

    with open(f"{args.data_path}/{args.annotation_name}.json", "w") as json_file:
        json.dump(annotations_coco, json_file)
    
    print(annotations_coco["categories"])