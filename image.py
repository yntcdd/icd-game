from PIL import Image
import os


os.makedirs("images/tiles/animated", exist_ok=True)

def split_sheet(sheet_path, output_prefix, frame_width, frame_height):
    sheet = Image.open(sheet_path)

    for frame in range(6):
        cropped = sheet.crop((
            frame * frame_width,
            0,
            (frame + 1) * frame_width,
            frame_height
        ))

        cropped.save(
            f"images/tiles/animated/{output_prefix}_{frame}.png"
        )

# BigDoor_D (36x36)
split_sheet(
    "images/tiles/animated/BigDoor_D.png",
    "BigDoor_D",
    36,
    36
)

# BigDoor_U (36x36)
split_sheet(
    "images/tiles/animated/BigDoor_U.png",
    "BigDoor_U",
    36,
    36
)

# BigDoor_S (30x42)
split_sheet(
    "images/tiles/animated/BigDoor_S.png",
    "BigDoor_S",
    30,
    42
)

# Create mirrored version for right-side doors
for frame in range(6):
    img = Image.open(
        f"images/tiles/animated/BigDoor_S_{frame}.png"
    )

    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)

    flipped.save(
        f"images/tiles/animated/BigDoor_A_{frame}.png"
    )

print("Done!")