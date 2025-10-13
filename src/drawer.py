from PIL.Image import new as new_image

from values import Component
from configs import DrawConfig, PTouchConfig

DEFAULT_CONFIG = PTouchConfig()

def generate_label(*components: Component, config: DrawConfig = DEFAULT_CONFIG):
    images = []
    heights = []

    for component in components:
        image = component.get_image(config)
        images.append(image)
        heights.append(image.height)

    total_height = sum(heights) + config.gap_block_px * (len(heights)-1)

    if total_height <= 0:
        return new_image("1", (config.width_px, 1), color="white")

    img = new_image("1", (config.width_px, total_height), color="white")

    y = 0
    for image, height in zip(images, heights):
        img.paste(image, (0, y))
        y += height + config.gap_block_px

    empty_rows_top = 0
    empty_rows_bottom = 0

    for y in range(img.height):
        if all(img.getpixel((x, y)) for x in range(img.width)):
            empty_rows_top += 1
        else:
            break

    for y in range(img.height-1, -1, -1):
        if all(img.getpixel((x, y)) for x in range(img.width)):
            empty_rows_bottom += 1
        else:
            break

    empty_rows = empty_rows_top + empty_rows_bottom
    if empty_rows:
        img = img.crop((0, empty_rows_top, img.width, img.height - empty_rows_bottom))

    img.save(config.path_save)
