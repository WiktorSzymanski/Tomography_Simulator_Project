from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np
from helpers.image_exec import bresenhams_line
import os
import streamlit as st
import math

IMAGE_DIR = "tomograf-zdjecia"

file_names = os.listdir(IMAGE_DIR)

selected_file_name = st.sidebar.selectbox("Input image", file_names, index=8)
selected_file_path = os.path.join(IMAGE_DIR, selected_file_name)

image = np.array(ImageOps.grayscale(Image.open(selected_file_path)))

image_width, image_height = np.shape(image)

center_x, center_y = int(image_width / 2), int(image_height / 2)

radius = np.ceil(np.sqrt(image_height * image_height +
             image_width * image_width) / 2)

st.write(f"""
Center: {center_x} {center_y}

Size:   {image_width} {image_height}

Radius: {radius}
""")

detectors_num = st.sidebar.slider("Number of detectors",
                                  min_value=10, max_value=360, value=360, step=10)
delta_alpha = st.sidebar.slider("Degree step between iteration",
                                min_value=0.1, max_value=30.0, step=0.1, value=0.8)
fi = st.sidebar.slider("Angular span of the detector - emitter system",
                       min_value=10, max_value=360, step=10, value=180)

st.write("""
# CT input image
""")

EMITTERS = []
DETECTORS = []
LINES = []

progress_bar_text = "Preparing scan"
progress_bar = st.progress(0, progress_bar_text)

st.image(image)

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



for scan in LINES:
    sinogram.append([])

    for line in scan:
        sum = 0
        for (x, y) in line:
            sum += image[x][y]

        if (len(line) == 0):
            sinogram[-1].append(sum)
        else:
            sinogram[-1].append(sum / len(line))

fig = plt.figure(figsize = (1,1))
plt.subplot(1, 1, 1);
plt.imshow(sinogram);
st.pyplot(fig)

# Filtering
# TODO

# Back projection
backprojected_img = np.zeros((image_height, image_width))

for i in range(len(sinogram)):
    for j in range(detectors_num):
        for (x,y) in LINES[i][j]:
            backprojected_img[x][y] += sinogram[i][j]


fig2 = plt.figure(figsize=(1,1))
plt.subplot(1, 1, 1);
plt.imshow(backprojected_img);
st.pyplot(fig2)
