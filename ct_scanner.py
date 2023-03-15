from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np
from lib.image import (bresenhams_line, image_filtering,
                       image_square, crop_to_original_size)


def ct_scan_simulation(image_path: str, delta_alpha: float, detectors_num: int, fi: int):

    image = Image.open(image_path)

    is_square, image_data = image_square(image)

    image = np.array(ImageOps.grayscale(image_data.get('image')))

    image_width, image_height = np.shape(image)

    center_x, center_y = int(image_width / 2), int(image_height / 2)

    radius = np.ceil(np.sqrt(image_height * image_height +
                             image_width * image_width) / 2)

    EMITTERS = []
    DETECTORS = []

    # Sinogram
    angles = np.arange(0, 360, delta_alpha)
    angles_num = len(angles)

    sinogram = np.zeros((angles_num, detectors_num))


    for step, angle_num in enumerate(range(angles_num)):
        alpha_rad = np.radians(angles[angle_num])
        fi_rad = np.radians(fi)

        E_x = int(radius * np.cos(alpha_rad)) + center_x
        E_y = int(radius * np.sin(alpha_rad)) + center_y
        emitter = (E_x, E_y)

        EMITTERS.append(emitter)
        DETECTORS.append([])

        for i in range(detectors_num):
            D_x = int(radius * np.cos(alpha_rad + np.pi - fi_rad / 2 +
                                      i * (fi_rad / (detectors_num - 1)))) + center_x
            D_y = int(radius * np.sin(alpha_rad + np.pi - fi_rad / 2 +
                                      i * (fi_rad / (detectors_num - 1)))) + center_y

            detector = (D_x, D_y)

            DETECTORS[-1].append(detector)

            line = bresenhams_line(
                emitter, detector,  image_height, image_width)

            sinogram_value = 0
            points = 0

            for (x, y) in line:
                sinogram_value += image[x][y]
                points += 1

            if points > 0:
                sinogram_value = sinogram_value / points

            sinogram[angle_num][i] = sinogram_value

    return (EMITTERS, DETECTORS, sinogram, (image_width, image_height), (is_square, image_data))


def backprojection(image_shape, sinogram, EMITTERS, DETECTORS):

    image_width, image_height = image_shape
    backprojected_img = np.zeros((image_height, image_width))

    for i in range(len(sinogram)):
        for j in range(len(sinogram[i])):
            for (x, y) in bresenhams_line(EMITTERS[i], DETECTORS[i][j], image_height, image_width):
                backprojected_img[x][y] += sinogram[i][j]

    return backprojected_img


def run(selected_file_path, delta_alpha, detectors_num, fi, filtering_config):
    

    EMITTERS, DETECTORS, sinogram, shape, (is_square, image_data) = ct_scan_simulation(
        selected_file_path, delta_alpha, detectors_num, fi)

    if filtering_config['use_filtering']:
        sinogram = image_filtering(sinogram, filtering_config['kernel_size'])

    # Back projection
    backprojected_img = backprojection(
        shape, sinogram, EMITTERS, DETECTORS)

    if (not is_square):
        backprojected_img = crop_to_original_size(
            backprojected_img, image_data.get('original_size'), image_data.get('offset'))

    return (sinogram, backprojected_img)
