import numpy as np
from PIL import Image

def bresenhams_line(start_point, end_point, height, width):
    points = []

    def get_pixel(i, j):
        if i >= 0 and i < width and j >= 0 and j < height:
            return (i, j)
        return None

    x1, y1 = start_point
    x2, y2 = end_point

    rise = y2 - y1
    run = x2 - x1

    if run == 0:
        if y2 < y1:
            y1, y2 = (y2, y1)
        for y in range(y1, y2 + 1):
            pixel = get_pixel(x1, y)

            if (pixel):
                points.append(pixel)
    else:
        m = float(rise) / run
        adjust = 1 if m >= 0 else -1
        offset = 0

        if m <= 1 and m >= -1:
            delta = abs(rise) * 2
            threshold = abs(run)
            threshold_inc = abs(run) * 2
            y = y1
            if x2 < x1:
                x1, x2 = (x2, x1)
                y = y2
            for x in range(x1, x2 + 1):
                pixel = get_pixel(x, y)

                if (pixel):
                    points.append(pixel)

                offset += delta
                if offset >= threshold:
                    y += adjust
                    threshold += threshold_inc
        else:
            delta = abs(run) * 2
            threshold = abs(rise)
            threshold_inc = abs(rise) * 2
            x = x1
            if y2 < y1:
                y1, y2 = (y2, y1)
                x = x2
            for y in range(y1, y2 + 1):
                pixel = get_pixel(x, y)

                if (pixel):
                    points.append(pixel)

                offset += delta
                if offset >= threshold:
                    x += adjust
                    threshold += threshold_inc

    return points

def create_kernel(kernel_size: int):
    kernel = list()

    for k in range(-(kernel_size // 2), int(np.ceil(kernel_size / 2))):
        if k == 0:
            kernel.append(1)
        else:
            kernel.append(0) if k % 2 == 0 else kernel.append((-4 / np.pi**2)/(k**2))

    return kernel


def image_filtering(sinogram, kernel_size):
    kernel = create_kernel(kernel_size)

    for i in range(len(sinogram)):
        sinogram[i] = np.convolve(sinogram[i], kernel, mode='same')

    return sinogram


def image_square(image):
    width, height = image.size

    if width == height:
        return True, {"image" : image}

    new_size = height if height > width else width
    squared_img = Image.new('RGB', (new_size, new_size), (0, 0, 0))

    sq_width, sq_height = squared_img.size
    offset = ((sq_width - width) // 2, (sq_height - height) // 2)

    squared_img.paste(image, offset)

    return False, {"image" : squared_img, "original_size" : (width, height), "offset" : offset}

def crop_to_original_size(image, original_size, offset):
    left = offset[0]
    bottom = offset[1]
    right = offset[0] + original_size[0]
    top = offset[1] + original_size[1]

    return image[bottom:top, left:right]
