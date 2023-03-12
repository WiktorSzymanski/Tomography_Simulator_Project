from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np
from helpers.image_exec import bresenhams_line, image_filtering
import os
import streamlit as st
import math

st.set_page_config(
    page_title="CT Scanner Simulation",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Made by [Adrian Kokot](https://github.com/AdrianKokot) and [Wiktor Szymański](https://github.com/WiktorSzymanski) for \"_Computer Science in Medicine_\" classes at Poznan University of Technology"
    }
)

IMAGE_DIR = "ct_examples"

file_names = os.listdir(IMAGE_DIR)

selected_file_name = st.sidebar.selectbox("Input image", file_names, index=8)
selected_file_path = os.path.join(IMAGE_DIR, selected_file_name)

image = np.array(ImageOps.grayscale(Image.open(selected_file_path)))

image_width, image_height = np.shape(image)

center_x, center_y = int(image_width / 2), int(image_height / 2)

radius = np.ceil(np.sqrt(image_height * image_height +
                         image_width * image_width) / 2)

# ct = st.container()

# info_container = ct.container()

# scan_container = ct.container()


def start_scan():

    EMITTERS = []
    DETECTORS = []
    LINES = []

    progress_bar_text = "Scanning"
    progress_bar = st.progress(0, progress_bar_text)

    for alpha in np.arange(0, 360, delta_alpha):
        alpha_rad = np.radians(alpha)
        fi_rad = np.radians(fi)

        E_x = int(radius * math.cos(alpha_rad)) + center_x
        E_y = int(radius * math.sin(alpha_rad)) + center_y

        EMITTERS.append((E_x, E_y))
        DETECTORS.append([])
        LINES.append([])

        for i in range(detectors_num):
            D_x = int(radius * math.cos(alpha_rad + math.pi - fi_rad / 2 +
                      i * (fi_rad / (detectors_num - 1)))) + center_x
            D_y = int(radius * math.sin(alpha_rad + math.pi - fi_rad / 2 +
                      i * (fi_rad / (detectors_num - 1)))) + center_y

            DETECTORS[-1].append((D_x, D_y))

            LINES[-1].append(bresenhams_line((E_x, E_y),
                                             (D_x, D_y), image_height, image_width))

        progress_bar.progress(alpha / 360.0, progress_bar_text)

    # Sinogram
    sinogram = []

    progress_bar_text = "Creating sinogram"
    progress_bar.progress(0, progress_bar_text)

    for i in range(len(LINES)):
        sinogram.append([])

        for line in LINES[i]:
            sum = 0
            for (x, y) in line:
                sum += image[x][y]

            if (len(line) == 0):
                sinogram[-1].append(sum)
            else:
                sinogram[-1].append(sum / len(line))

        progress_bar.progress((i + 1) / len(LINES), progress_bar_text)

    fig_unfiltered, (ax_sinogram, ax_image) = plt.subplots(1, 2)
    ax_sinogram.imshow(sinogram, 'gray')

    # Back projection
    backprojected_img = np.zeros((image_height, image_width))
    progress_bar_text = "Back projection"
    progress_bar.progress(0, progress_bar_text)

    for i in range(len(sinogram)):
        for j in range(detectors_num):
            for (x, y) in LINES[i][j]:
                backprojected_img[x][y] += sinogram[i][j]

        progress_bar.progress((i + 1) / len(sinogram), progress_bar_text)

    ax_image.imshow(backprojected_img, 'gray')
    st.write("## Unfiltered")
    st.pyplot(fig_unfiltered)

    progress_bar.progress(0, "Filtering sinogram")
    sinogram = image_filtering(sinogram, kernel_size)
    progress_bar.progress(1, "Filtering sinogram")

    fig_filtered, (ax_sinogram, ax_image) = plt.subplots(1, 2)

    ax_sinogram.imshow(sinogram, 'gray')

    # sinogram_col, image_col = scan_container.container().columns(2)

    # Filtering

    # Back projection
    backprojected_img = np.zeros((image_height, image_width))

    progress_bar_text = "Back projection for filtered sinogram"
    progress_bar.progress(0, progress_bar_text)

    for i in range(len(sinogram)):
        for j in range(detectors_num):
            for (x, y) in LINES[i][j]:
                backprojected_img[x][y] += sinogram[i][j]

        progress_bar.progress((i + 1) / len(sinogram), progress_bar_text)

    ax_image.imshow(backprojected_img, 'gray')
    st.write("## Filtered")
    st.pyplot(fig_filtered)

    # sinogram = np.array(sinogram)

    # if wdg_filtering.value:
    #     kernel = []
    #     for k in range(-int(np.floor(kernel_size/2)), int(np.ceil(kernel_size/2))):
    #         if k == 0:
    #             kernel.append(1)
    #         else:
    #             if k % 2 == 0:
    #                 kernel.append(0)
    #             else:
    #                 kernel.append((-4 / np.pi**2)/(k**2))

    #     for i in range(len(sinogram)):
    #         sinogram[i] = np.convolve(sinogram[i], kernel, mode='same')

    #     plt.imshow(sinogram, cmap='gray')
    #     plt.show()


# Input values
detectors_num = st.sidebar.slider("Number of detectors",
                                  min_value=10, max_value=360, value=360, step=10)
delta_alpha = st.sidebar.slider("Degree step between iteration",
                                min_value=0.1, max_value=30.0, step=0.1, value=0.8)
fi = st.sidebar.slider("Angular span of the detector - emitter system",
                       min_value=10, max_value=360, step=10, value=180)

kernel_size = st.sidebar.slider(
    "Filtering kernel size", min_value=3, max_value=150, step=2, value=50)

start_scan_button = st.sidebar.button('Start scan', on_click=start_scan)

# Container


# info_container_left_col, info_container_right_col = info_container.columns(2)

st.header("Loaded data information")

st.write(f"""
Image size: {image_width} {image_height}

Center: {center_x} {center_y}

Radius: {radius}
""")

st.image(image)
