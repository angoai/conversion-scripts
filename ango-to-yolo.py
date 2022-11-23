import os
import json


def ango_to_yolo(json_file_path, output_folder):
    # Read JSON file
    f = open(json_file_path, encoding="utf8")
    ango_data = json.load(f)
    f.close()

    # Create folder if it doesn't exist
    if not os.path.exists(yolo_folder):
        os.mkdir(yolo_folder)

    for index, asset in enumerate(ango_data):
        external_id = asset['externalId']
        objects = asset['tasks'][0]['objects']

        line_list = []
        for obj in objects:
            if "bounding-box" in obj:
                class_name =  obj['title']
                x, y = obj["bounding-box"]['x'], obj["bounding-box"]['y']
                width, height = obj["bounding-box"]['width'], obj["bounding-box"]['height']

                parts = [class_name, str(x), str(y), str(width), str(height), '\n']

                line = ' '.join(parts)
                line_list.append(line)

        output_file_path = os.path.join(output_folder, external_id + '.txt')

        f = open(output_file_path, "w", encoding="utf8")
        f.writelines(line_list)
        f.close()


if __name__ == "__main__":
    json_path = '<YOUR INPUT JSON FILE PATH>'
    yolo_folder = '<YOUR OUTPUT FOLDER>'
    
    ango_to_yolo(json_path, yolo_folder)
