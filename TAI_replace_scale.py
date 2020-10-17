import cv2
import numpy as np
from PIL import Image
import glob
import timeit
import os


def replace_scale():
    InputPath = input('Input Path=?\n')
    OutputPath = input('Output Path=?\n')
    all_file = glob.glob('./' + InputPath + '/*.tif')
    for filename in all_file:

        start = timeit.default_timer()

        img_original = cv2.imread(filename)
        img_original_gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
        # img_original_gray_dn = cv2.fastNlMeansDenoising(img_original_gray, None, 20, 5, 15)
        scale_original = cv2.imread('./scale/dpi300.tif', 0)

        res = cv2.matchTemplate(img_original_gray, scale_original, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_point, max_point = cv2.minMaxLoc(res)
        top_left = max_point

        if max_val < 0.8:
            with open('val_lower_than_0point8.txt', mode='a') as F:
                F.write(filename + ' Max_val = ' + str(max_val) + '\n')

        rgb_size = 30
        rgb_values = img_original[top_left[1] - rgb_size:top_left[1], top_left[0]:top_left[0] + rgb_size]

        mean_blue = int(np.round(np.mean(rgb_values[:, :, 0])))
        mean_green = int(np.round(np.mean(rgb_values[:, :, 1])))
        mean_red = int(np.round(np.mean(rgb_values[:, :, 2])))

        del img_original
        del img_original_gray
        del scale_original

        base_image = Image.open(filename)
        scale_original_4c = Image.open('./scale/dpi300_alpha.tif')
        watermark = Image.open('./scale/dpi600.tif')
        width, height = base_image.size
        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        transparent.paste((mean_red, mean_green, mean_blue, 255), top_left, mask=scale_original_4c)
        transparent.paste(watermark, top_left, mask=watermark)
        transparent.save('./' + OutputPath + '/' + os.path.basename(filename), compression='tiff_jpeg', quality=100, dpi=(300, 300))

        stop = timeit.default_timer()

        print(os.path.basename(filename) + ' is ok! / Max_val = ' + str(max_val) + ' / time : ' + str(stop-start))


if __name__ == '__main__':
    replace_scale()
    exit_program = input('press enter to quit')


