import numpy as np
from PIL import Image, ImageOps

from matplotlib import pyplot as plt
from matplotlib import image as mpimg

from lib.history_saver import HistorySaver

from ct_scanner import run

statistics_saver = HistorySaver('./statistics_data')
statistics_saver.clear_history()

images_path = './ct_examples/'

image = None

def run_statistics(img_name, delta_alpha, detectors_num, fi, filtering_config):
  _, backprojected_img = run(images_path + img_name + '.jpg', delta_alpha, detectors_num, fi, filtering_config)

  with open(f"./statistics_data/RMSE-{img_name}-{round(delta_alpha,2)}-{detectors_num}-{fi}-{'wF' if filtering_config['use_filtering'] else 'nF'}", 'w') as file:
    file.write(str(calc_RMSE(image, backprojected_img)))


def calc_RMSE(true_data, pred_data):
  return np.sqrt(np.square(np.subtract(true_data, pred_data)).mean())

if __name__ == '__main__':
  img_name = 'Shepp_logan'

  detectors = np.arange(90, 721, 90)
  alphas = np.array(list(map(lambda x: 360/x ,np.arange(90, 721, 90))))
  fis = np.arange(45, 271, 45)
  filtering_configs = [{'use_filtering': True, 'kernel_size': 15}, {'use_filtering': False}]

  image = np.array(ImageOps.grayscale(Image.open(images_path + img_name + '.jpg')))

  for detector in detectors:
    for alpha in alphas:
      for fi in fis:
        for filtering_config in filtering_configs:
          run_statistics(img_name, alpha, detector, fi, filtering_config)
        print(f'\t\tfi {fi} done')
      print(f'\talpha {alpha} done')
    print(f'detectors {detector} done')
    