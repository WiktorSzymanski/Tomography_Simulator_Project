from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np
from helpers.image_exec import (
    bresenhams_line,
    image_filtering,
    image_square,
    crop_to_original_size)
import streamlit as st
from helpers.dicom import save_as_dicom
import ui

simulation_tab, dicom_tab = ui.setup()

scan_form = st.session_state

if not scan_form.scan_started:
    st.stop()


@st.cache_data(show_spinner=False)
def ct_scan_simulation(image_path: str, delta_alpha: float, detectors_num: int, fi: int):
    progress_bar = st.progress(0.0)

    def progress_callback(progress):
        progress = progress * 1.0
        progress_bar.progress(
            progress, "Scanning {0:.2f}%".format(progress * 100.0))

        if progress == 1:
            progress_bar.empty()

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
    sinogram_history = []

    progress_callback(0)

    for angle_num in range(angles_num):
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

        progress_callback((angle_num + 1) / angles_num)
        sinogram_history.append(np.copy(sinogram))

    progress_callback(1)

    return (EMITTERS, DETECTORS, sinogram, sinogram_history, (image_width, image_height), (is_square, image_data))


@st.cache_data(show_spinner=False)
def backprojection(image_shape, sinogram, EMITTERS, DETECTORS):
    progress_bar = st.progress(0.0)

    def progress_callback(progress):
        progress = progress * 1.0
        progress_bar.progress(
            progress, "Back projection {0:.2f}%".format(progress * 100.0))

        if progress == 1:
            progress_bar.empty()

    image_width, image_height = image_shape
    backprojected_img = np.zeros((image_height, image_width))

    backprojection_history = []
    progress_callback(0)

    for i in range(len(sinogram)):
        for j in range(len(sinogram[i])):
            for (x, y) in bresenhams_line(EMITTERS[i], DETECTORS[i][j], image_height, image_width):
                backprojected_img[x][y] += sinogram[i][j]

        backprojection_history.append(np.copy(backprojected_img))
        progress_callback((i + 1) / len(sinogram))

    progress_callback(1)

    return (backprojected_img, backprojection_history)


@st.cache_data(show_spinner=False)
def run(selected_file_path, delta_alpha, detectors_num, fi, filtering_config, dicom_config):

    EMITTERS, DETECTORS, sinogram, sinogram_history, shape, (is_square, image_data) = ct_scan_simulation(
        selected_file_path, delta_alpha, detectors_num, fi)

    if filtering_config['use_filtering']:
        sinogram = image_filtering(sinogram, filtering_config['kernel_size'])

    # Back projection
    backprojected_img, backprojection_history = backprojection(
        shape, sinogram, EMITTERS, DETECTORS)

    if (not is_square):
        backprojected_img = crop_to_original_size(
            backprojected_img, image_data.get('original_size'), image_data.get('offset'))

    if dicom_config['use_dicom']:
        save_as_dicom("dicom_examples/" + dicom_config['dicom_file_name'], backprojected_img, {
            "PatientName": dicom_config['patient_name'],
            "PatientBirthDate": dicom_config['patient_birth_date'],
            "PatientID": dicom_config['patient_id'],
            'ImageComments': dicom_config['image_comments'],
            "StudyDate": dicom_config['study_date']
        })

    return (sinogram, sinogram_history, backprojected_img, backprojection_history)


filtering_config = {
    'use_filtering': scan_form.use_filtering
}
dicom_config = {
    'use_dicom': scan_form.use_dicom
}

if filtering_config['use_filtering']:
    filtering_config.update({'kernel_size': scan_form.kernel_size})

if dicom_config['use_dicom']:
    dicom_config.update({'dicom_file_name': scan_form.dicom_file_name,
                         'patient_name': scan_form.patient_name,
                         'patient_birth_date': scan_form.patient_birth_date,
                         'patient_id': scan_form.patient_id,
                         'image_comments': scan_form.image_comments,
                         'study_date': scan_form.study_date})


sinogram, sinogram_history, backprojected_img, backprojection_history = run(
    scan_form.image_path, scan_form.delta_alpha, scan_form.number_of_detectors, scan_form.fi, filtering_config, dicom_config)

fig, (ax_sinogram, ax_image) = plt.subplots(1, 2)

show_steps = simulation_tab.checkbox("Show steps")

if show_steps:
    step_num = simulation_tab.slider(
        "Step number",
        min_value=0,
        max_value=len(sinogram_history) - 1,
        step=1,
        value=len(sinogram_history) - 1
    )

    ax_sinogram.imshow(sinogram_history[step_num], 'gray')
    ax_image.imshow(backprojection_history[step_num], 'gray')
else:
    ax_sinogram.imshow(sinogram, 'gray')
    ax_image.imshow(backprojected_img, 'gray')

ax_sinogram.axis('off')
ax_image.axis('off')

simulation_tab.pyplot(fig)
