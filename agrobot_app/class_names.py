import os

dataset_dir = r"C:\Users\Admin\Downloads\PlantVillage"
class_names = sorted([d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))])

with open(r"d:\Testing_Agrobot\Agro_Bot\agrobot_app\class_names.txt", "w", encoding="utf-8") as f:
    for name in class_names:
        f.write(name + "\n")

print("class_names.txt created with these classes:")
for name in class_names:
    print(name)