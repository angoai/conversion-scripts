import os
import json
from tqdm import tqdm
from skimage.io import imread


def ango_to_yolo(json_file_path, output_folder, data_dir=None):
    # Read JSON file
    f = open(json_file_path, encoding="utf8")
    ango_data = json.load(f)
    f.close()

    # Create folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    for index, asset in enumerate( tqdm(ango_data) ):
        data_url = asset['asset']
        external_id = asset['externalId']
        objects = asset['tasks'][0]['objects']
        
        image_height, image_width = 0, 0
        dimension_flag = False
        if 'metadata' in asset:
            if ('width' in asset['metadata']) & ('height' in asset['metadata']):
                image_width = asset['metadata']['width']
                image_height = asset['metadata']['height']
                dimension_flag = True
        
        if (not dimension_flag) & (data_dir is not None):
            local_data_path = os.path.join(data_dir, external_id)
            img = imread(local_data_path)
            image_height, image_width = img.shape[0:2]
            dimension_flag = True
        
        if not dimension_flag:
            img = imread(data_url)
            image_height, image_width = img.shape[0:2]
        
        line_list = []
        for obj in objects:
            if "bounding-box" in obj:
                class_name =  obj['title']
                
                x, y = obj["bounding-box"]['x'], obj["bounding-box"]['y']
                width, height = obj["bounding-box"]['width'], obj["bounding-box"]['height']
                
                x_centre = x + width/2
                y_centre = y + height/2
                
                x_centre_norm = round(x_centre / image_width, 6)
                y_centre_norm = round(y_centre / image_height, 6)
                width_norm = round(width / image_width, 6)
                height_norm = round(height / image_height, 6)
                
                parts = [class_id, str(x_centre_norm), str(y_centre_norm), str(width_norm), str(height_norm)]
                
                line = ' '.join(parts) + '\n'
                line_list.append(line)
        
        #output_file_path = os.path.join(output_folder, external_id.split('.')[0] + '.txt')
        output_file_path = os.path.join(output_folder, external_id + '.txt')
        
        f = open(output_file_path, "w", encoding="utf8")
        f.writelines(line_list)
        f.close()


if __name__ == "__main__":
    json_path = '<YOUR INPUT JSON FILE PATH>'
    yolo_folder = '<YOUR OUTPUT FOLDER>'
    
    ango_to_yolo(json_path, yolo_folder)
