import pandas as pd
import json
import os

csv_reader = pd.read_csv('/app/code/CCTV_IP_Details_Zojila.csv')

with open('/app/code/header.json', 'r') as f:
    header_config = json.load(f)

with open('/app/code/structure.json', 'r') as f:
    base_camera_config = json.load(f)

server_mapper = {}

for index, row in csv_reader.iterrows():
    server = row['Server']
    username = row['USER NAME']
    password = row['PASSWORD']
    camera_ip_address = row['IP Address']
    rtsp_url = f"rtsp://{username}:{password}@{camera_ip_address}:554/"

    if server not in server_mapper:
        server_mapper[server] = []

    camera_config = base_camera_config.copy()

    camera_config["video_src"] = rtsp_url
    camera_config["lane_name"] = row['Tag Number']
    camera_config["request_code"] = f"{row['Tag Number']}-EX-LHS"
    camera_config["loc_name"] = row['Item Name']
    camera_config["camera_orientation"] = "front"
    camera_config["post_url"] = "http://192.168.200.83:8082/apiv2/tollvehiclealpr"

    server_mapper[server].append(camera_config)

for server, cameras in server_mapper.items():
    batch_size = 8
    total_batches = (len(cameras) + batch_size - 1) // batch_size

    os.makedirs('/app/code/output_jsons', exist_ok=True)

    for batch_num in range(total_batches):
        batch_cameras = cameras[batch_num * batch_size: (batch_num + 1) * batch_size]
        json_data = header_config.copy()
        json_data["camera_list"] = batch_cameras

        json_filename = f"/app/code/output_jsons/{server}_config{batch_num + 1}.json"
        with open(json_filename, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        print(f"Saved {json_filename} with {len(batch_cameras)} cameras.")
