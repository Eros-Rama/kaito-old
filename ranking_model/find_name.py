import os
import json


class find_name:
    def check_find_name(self, str):
        root_dir = __file__.split("ranking_model")[0]
        output_file_path = root_dir + "denver_speaker_name.json"
        with open(output_file_path, "r") as file:
            doc = json.load(file)
        name_list = doc["names"]
        # print (name_list[:5])
        for name in name_list:
            if name in str:
                matched_name = name
                return matched_name
        return None 



# if __name__ == "__main__":
#     en = find_name()
#     query = "What does SPEAKER_23's think about the influence of in global practices?"
#     ans = en.check_find_name(query)
#     print(ans)