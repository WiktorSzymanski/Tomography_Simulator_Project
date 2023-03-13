import streamlit as st
import os
import datetime
import pydicom

IMAGE_DIR = "ct_examples"
DICOM_DIR = "dicom_examples"


def setup_image_path():
    st.session_state.image_path = os.path.join(
        IMAGE_DIR,
        st.session_state.image_file_name
    )


def reset_submit():
    st.session_state.scan_started = False


def setup():
    st.set_page_config(
        page_title="CT Scanner Simulation",
        page_icon="🧠",
        menu_items={
            'About': "Made by [Adrian Kokot](https://github.com/AdrianKokot) and [Wiktor Szymański](https://github.com/WiktorSzymanski) for \"_Computer Science in Medicine_\" classes at Poznan University of Technology"
        }
    )

    st.title("CT Scanner Simulation")

    simulation_tab, dicom_tab = st.tabs(["Simulation", "Read DICOM"])

    if 'scan_started' not in st.session_state:
        reset_submit()

    form_container = simulation_tab.expander(
        label="Simulation data form", expanded=not st.session_state.scan_started)

    form_container.selectbox(
        "Input file",
        os.listdir(IMAGE_DIR),
        key='image_file_name',
        on_change=reset_submit
    )

    setup_image_path()

    form_container.slider(
        "Number of detectors",
        min_value=10,
        max_value=360,
        value=360,
        step=10,
        key='number_of_detectors',
        on_change=reset_submit
    )

    form_container.slider(
        "Degree step between iteration",
        min_value=0.1,
        max_value=30.0,
        step=0.1,
        value=0.8,
        key='delta_alpha',
        on_change=reset_submit
    )

    form_container.slider(
        "Angular span of the detector - emitter system",
        min_value=10,
        max_value=360,
        step=10,
        value=180,
        key='fi',
        on_change=reset_submit
    )

    form_container.checkbox("Use filtering", key='use_filtering',
                            on_change=reset_submit)

    if st.session_state.use_filtering:
        form_container.slider(
            "Filtering kernel size",
            key='kernel_size',
            min_value=3,
            max_value=150,
            step=2,
            value=15,
            on_change=reset_submit
        )

    form_container.checkbox(
        "Save file as dicom",
        key='use_dicom',
        on_change=reset_submit
    )

    if st.session_state.use_dicom:
        form_container.subheader("Patient data")

        form_container.text_input(
            "Patient ID",
            key='patient_id',
            on_change=reset_submit
        )

        form_container.text_input(
            "Patient Name",
            key='patient_name',
            on_change=reset_submit
        )

        patient_birth_date = form_container.date_input(
            "Patient Birth Date",
            datetime.date.today(),
            on_change=reset_submit
        )

        if patient_birth_date:
            st.session_state.patient_birth_date = patient_birth_date.strftime("%Y%m%d")

        study_date = form_container.date_input(
            "Study Date",
            datetime.date.today(),
            on_change=reset_submit
        )

        if study_date:
            st.session_state.study_date = study_date.strftime("%Y%m%d")

        form_container.text_area(
            "Image Comments",
            key='image_comments',
            on_change=reset_submit
        )

        form_container.text_input(
            "Output file name",
            key='dicom_file_name',
            on_change=reset_submit
        )

    submitted = form_container.button("Start scan")
    if submitted:
        st.session_state.scan_started = True

    dicom_file_name = dicom_tab.selectbox(
        "Input file",
        os.listdir(DICOM_DIR)
    )

    dicom_file_path = os.path.join(DICOM_DIR, dicom_file_name)

    ds = pydicom.dcmread(dicom_file_path)

    dicom_tab.header("Image")

    dicom_tab.image(ds.pixel_array)

    dicom_tab.subheader("DICOM File data")
    dicom_tab.text(ds)

    return (simulation_tab, dicom_tab)
