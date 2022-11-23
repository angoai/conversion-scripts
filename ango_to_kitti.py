import os
import json


def create_kitti_file(asset):
    truncation = '0.00'
    occlusion = 0
    alpha = '0.00'
    height = '0.00'
    width = '0.00'
    length = '0.00'
    x_3d = '0.00'
    y_3d = '0.00'
    z_3d = '0.00'
    rotation_y = '0.00'
    kitti_lines = []
    for obj in asset['tasks'][0]['objects']:
        if "bounding-box" in obj:
            class_name =  obj['title']
            x_min, y_min = int(obj["bounding-box"]['x']), int(obj["bounding-box"]['y'])
            bbox_width, bbox_height = int(obj["bounding-box"]['width']), int(obj["bounding-box"]['height'])
            x_max, y_max = x_min + bbox_width, y_min + bbox_height
            
            line = f"{class_name} {truncation} {occlusion} {alpha} {x_min} {y_min} {x_max} {y_max} {height} {width} {length} {x_3d} {y_3d} {z_3d} {rotation_y}\n"
            kitti_lines.append(line)
    return kitti_lines, f"{asset['externalId'].split('.')[0]}.txt"


def write_kitti_file(directory, file_name, lines):
    f = open(os.path.join(directory,file_name), 'w')
    f.writelines(lines)
    f.close()


def ango_to_kitti(json_file_path, kitti_folder):
    # Read json file
    f = open(json_file_path, encoding="utf8")
    ango_data = json.load(f)
    f.close()
    
    # Create folder if it doesn't exist
    if not os.path.exists(kitti_folder):
        os.mkdir(kitti_folder)
    
    # For each asset, convert annotations to KITTI format
    for asset in ango_data:
        kitti_lines,file_name = create_kitti_file(asset)
        write_kitti_file(kitti_folder, file_name,kitti_lines)


if __name__ == "__main__":
    input_json_file = '<YOUR INPUT JSON FILE>'
    output_folder = '<YOUR OUTPUT FOLDER>'
    
    ango_to_kitti(input_json_file, output_folder)
