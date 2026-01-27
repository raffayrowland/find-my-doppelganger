import csv
import os
import kagglehub
from pathlib import Path
import shutil

# Download database
root = Path(kagglehub.dataset_download("xhlulu/140k-real-and-fake-faces"))
print(f"Downloaded to  {root} \n")

realFiles = []

# CSVs that contain paths to images
csvPaths = [
    os.path.join(root, "test.csv"),
    os.path.join(root, "train.csv"),
    os.path.join(root, "valid.csv")
]

# Save the path of real images in each CSV
# row[4] = real/fake, row[5] is relative path to image
for csvPath in csvPaths:
    with open(csvPath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[4] == "real":
                realFiles.append(os.path.join(root, "real_vs_fake/real-vs-fake", row[5]))

print(len(realFiles))
print(realFiles[0])

moved = 0
missing = 0

destination = Path("dataset")
destination.mkdir(parents=True, exist_ok=True)
name = 0

for file in realFiles:
    if not os.path.exists(file):
        missing += 1
        continue

    # Move each realFile to our dataset, with new name
    shutil.move(str(file), str(destination / str(name)))
    name += 1
    moved += 1

print(f"Moved {moved} out of {len(realFiles)} files with {missing} missing")
shutil.rmtree(root)
print("Deleted dataset download folder:", root)