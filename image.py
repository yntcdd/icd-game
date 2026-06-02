from PIL import Image
import os

folder = "images/tiles/tiles"

for filename in os.listdir(folder):
    if filename.lower().endswith((".png", ".gif", ".jpg", ".jpeg")):
        path = os.path.join(folder, filename)

        try:
            img = Image.open(path)
            img = img.resize((64, 64), Image.NEAREST)
            img.save(path)  # overwrite original

            print(f"Resized: {filename}")

        except Exception as e:
            print(f"Failed: {filename} ({e})")

print("Done!")