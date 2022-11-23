import os
import json
from tqdm import tqdm
from datetime import date
from skimage.io import imread
from shapely.geometry import Polygon


def create_info():
    return {"description": "Annotation by Ango AI",
            "url": "https://ango.ai",
            "version": "1.0",
            "year": int(date.today().strftime("%Y")),
            "contributor": "Ango AI",
            "date_created": date.today().strftime("%Y/%m/%d")}


def create_categories(input_category_list):
    categories = []
    for category_id, category_name in enumerate(input_category_list):
        categories.append({"id": category_id+1, 
                           "supercategory": "object", 
                           "name": category_name})
    return categories


def create_object_list(asset):
    objs = []
    # Standardize segmentations and polygon tools
    # Since COCO only works with polygons
    for obj in asset['tasks'][0]['objects']:
        if "segmentation" in obj:
            objs.append({"polygon": obj['segmentation']['zones'][0]['region'], 
                         "title": obj['title'],
                         "schemaId": obj['schemaId']})
        elif "polygon" in obj:
            objs.append({"polygon": obj['polygon'], 
                         "title": obj['title'],
                         "schemaId": obj['schemaId']})
        elif "bounding-box" in obj:
            x,y = int(obj["bounding-box"]['x']),int(obj["bounding-box"]['y'])
            w,h = int(obj["bounding-box"]['width']), int(obj["bounding-box"]['height'])
            box_pg = [[x,y], [x,y+h], [x+w,y+h], [x+w,y], [x,y]]
            objs.append({"polygon": box_pg, 
                         "title": obj['title'],
                         "schemaId": obj['schemaId']})
    return objs


def create_coco_segmentation(input_object):
    curr_seg = [[]]
    for point in input_object['polygon']:
        curr_seg[0].append(round(point[0], 2))
        curr_seg[0].append(round(point[1], 2))
    return curr_seg


def create_images_and_annotations(json_data, category_list, data_dir=None):
    images = []
    annotations = []
    annotation_index = 1
    for image_index, asset in enumerate( tqdm(json_data) ):
        data_url = asset['asset']
        file_name = asset['externalId']
        date_captured = asset['labeledAt']
        date_captured = date_captured.replace('T', ' ')
        date_captured = date_captured[:-5]
        
        height, width = 0, 0
        dimension_flag = False
        if 'metadata' in asset:
            if ('width' in asset['metadata']) & ('height' in asset['metadata']):
                width = asset['metadata']['width']
                height = asset['metadata']['height']
                dimension_flag = True
        
        if (not dimension_flag) & (data_dir is not None):
            local_data_path = os.path.join(data_dir, file_name)
            img = imread(local_data_path)
            height, width = img.shape[0:2]
            dimension_flag = True
            
        if not dimension_flag:
            img = imread(data_url)
            height, width = img.shape[0:2]

        images.append({"license": 0,
                       "file_name": file_name,
                       "coco_url": data_url,
                       "height": height,
                       "width": width,
                       "date_captured": date_captured,
                       "id": image_index+1})
        
        objects = create_object_list(asset)
        for obj in objects:
            segmentation = create_coco_segmentation(obj)
            polygon = Polygon(obj['polygon'])
            area = polygon.area
            minx, miny, maxx, maxy = polygon.bounds
            bb = [round(minx, 2), round(miny, 2), round(maxx-minx, 2), round(maxy-miny, 2)]
            category_id = category_list.index(obj['title']) + 1
            annotations.append({"segmentation": segmentation,
                                "area": area,
                                "iscrowd": 0,
                                "image_id": image_index+1,
                                "bbox": bb,
                                "category_id": category_id,
                                "id": annotation_index})
            annotation_index = annotation_index + 1
    
    return images, annotations


def ango_to_coco(input_json_file, output_coco_file, category_list, data_dir=None):
    # Read JSON File
    if not os.path.exists(input_json_file):
        raise ValueError('JSON file does not exist!')
    
    f = open(input_json_file, encoding="utf8")
    json_data = json.load(f)
    f.close()
    
    # Convert Ango to COCO
    info = create_info()
    images, annotations = create_images_and_annotations(json_data, category_list, data_dir)
    categories = create_categories(category_list)
    coco_data = {"info": info,
                 "licenses": [],
                 "images": images,
                 "annotations": annotations,
                 "categories": categories}

    # Write to file
    with open(output_coco_file, 'w') as outfile:    
        json.dump(coco_data, outfile)


if __name__ == "__main__":
    json_file = '<YOUR INPUT JSON FILE PATH>'
    coco_file = '<YOUR OUTPUT JSON FILE PATH>'
    data_directory = "<YOUR DATA DIRECTORY>"
    class_names = ['class_1', 'class_2', 'class_3']
    
    ango_to_coco(json_file, coco_file, class_names, data_directory)
