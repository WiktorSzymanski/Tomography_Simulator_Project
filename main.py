from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np
from helpers.image_exec import bresenhams_line, image_filtering
import os
import io
import streamlit as st
import math
from helpers.dicom import save_as_dicom
import pydicom
import datetime

st.set_page_config(
    page_title="CT Scanner Simulation",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Made by [Adrian Kokot](https://github.com/AdrianKokot) and [Wiktor Szymański](https://github.com/WiktorSzymanski) for \"_Computer Science in Medicine_\" classes at Poznan University of Technology"
    }
)

images_tab, dicom_tab = st.sidebar.tabs(["Image", "DICOM"])

IMAGE_DIR = "ct_examples"

selected_file_name = images_tab.selectbox("Input file", os.listdir(IMAGE_DIR))
selected_file_path = os.path.join(IMAGE_DIR, selected_file_name)

uploaded_file = dicom_tab.file_uploader("Choose a file")

info_container = st.container()

# Input values
detectors_num = images_tab.slider("Number of detectors",
                                  min_value=10, max_value=360, value=360, step=10)
delta_alpha = images_tab.slider("Degree step between iteration",
                                min_value=0.1, max_value=30.0, step=0.1, value=0.8)
fi = images_tab.slider("Angular span of the detector - emitter system",
                       min_value=10, max_value=360, step=10, value=180)

use_filtering = images_tab.checkbox("Use filtering")

if use_filtering:
    kernel_size = images_tab.slider(
        "Filtering kernel size", min_value=3, max_value=150, step=2, value=50)

use_dicom = images_tab.checkbox("Save file as dicom")

if use_dicom:
    images_tab.subheader("Patient data")

    patient_id = images_tab.text_input("Patient ID")
    patient_name = images_tab.text_input("Patient Name")
    patient_age = images_tab.number_input("Patient Age", step=1)
    study_date = images_tab.date_input("Image Date", datetime.date.today())
    image_comments = images_tab.text_area("Image Comments")
    file_name = images_tab.text_input("Output file name")


def scan():
    image = np.array(ImageOps.grayscale(Image.open(selected_file_path)))

    image_width, image_height = np.shape(image)

    center_x, center_y = int(image_width / 2), int(image_height / 2)

    radius = np.ceil(np.sqrt(image_height * image_height +
                            image_width * image_width) / 2)

    info_container = st.container()

    info_container_left_col, info_container_right_col = info_container.columns(2)

    info_container_left_col.header("Loaded data information")

    info_container_left_col.write(f"""
    Image size: {image_width} {image_height}

    Center: {center_x} {center_y}

    Radius: {radius}
    """)

    info_container_right_col.image(image)

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

    save_as_dicom("test.dcm", backprojected_img, {
        "PatientName": "TEST",
        "PatientAge": "TEST",
        "PatientSex": "TEST",
        "PatientID": "TEST",
        'ImageComments': "TEST",
        "StudyDate": "TEST"
    })

images_tab.button('Start scan', on_click=scan)

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    dicom_file = io.BytesIO(bytes_data)
    ds = pydicom.dcmread(dicom_file)

    info_container.header("DICOM Image")

    info_container.image(ds.pixel_array)

    info_container.subheader("DICOM File data")
    info_container.text(ds)
