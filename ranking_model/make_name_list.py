from pathlib import Path
import json
root_dir = __file__.split("ranking_model")[0]
dataset_path = root_dir + "datasets/eth_denver_dataset"
dataset_path = Path(dataset_path)


all_files = dataset_path.glob("*.json")
names = []
cnt = 0
for i, file in enumerate(all_files) :
    with open(file, "r") as f:
        name = json.load(f)
        if name["speaker"] in names:
             continue
        names.append(name["speaker"])
        cnt += 1


# print(names)
doc = {}
doc["names"] = names
# print(cnt)
output_file_path = root_dir + "denver_speaker_name.json"
with open(output_file_path, "w") as f:
        json.dump(doc, f, indent=4)

