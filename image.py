from PIL import Image

INPUT_DIR = "images/gui/interface"
FILES = ["Tile_04.png", "Tile_05.png", "Tile_06.png"]

SCALE = 4

def load_and_scale(path):
    img = Image.open(path).convert("RGBA")
    new_size = (img.width * SCALE, img.height * SCALE)
    return img.resize(new_size, Image.NEAREST)

def main():
    images = [load_and_scale(f"{INPUT_DIR}/{f}") for f in FILES]

    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    result = Image.new("RGBA", (total_width, max_height))

    x_offset = 0
    for img in images:
        result.paste(img, (x_offset, 0))
        x_offset += img.width

    result.save(f"{INPUT_DIR}/combined_04_05_06.png")

if __name__ == "__main__":
    main()