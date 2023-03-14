import os
import numpy as np
import streamlit as st
import shutil

@st.cache_resource
class HistorySaver:

    def __init__(self, path='./history'):
        self.path = path

    def how_many_steps(self, name):
        path = f'{self.path}/{name}'

        return len(os.listdir(path))

    def save_history(self, name, angle, data):
        path = f'{self.path}/{name}'

        if not os.path.exists(path):
            os.mkdir(path)

        np.savetxt(f'{path}/{angle}.txt', data, fmt='%d')

    def load_history(self, name, angle):
        return np.loadtxt(f'{self.path}/{name}/{angle}.txt', dtype=int)
    
    def clear_history(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.mkdir(self.path)
