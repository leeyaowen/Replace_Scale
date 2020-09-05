import cv2
import numpy as np
from PIL import Image
import glob


def replace_scale():
    all_file = glob.glob('*.tif')
    for filename in all_file:

        img_original_3c = cv2.imread('./' + filename)
        img_original_scale_3c = cv2.imread('./scale/dpi300.tif')

        res = cv2.matchTemplate(img_original_3c, img_original_scale_3c, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_point, max_point = cv2.minMaxLoc(res)
        top_left = max_point

        img_original = cv2.cvtColor(img_original_3c, cv2.COLOR_BGR2BGRA)
        del img_original_scale_3c

        rgb_size = 30
        rgb_values = img_original[top_left[1]-rgb_size:top_left[1], top_left[0]:top_left[0]+rgb_size]

        mean_blue = int(np.round(np.mean(rgb_values[:, :, 0])))
        mean_green = int(np.round(np.mean(rgb_values[:, :, 1])))
        mean_red = int(np.round(np.mean(rgb_values[:, :, 2])))

        base_image = Image.open('./' + filename)
        img_original_scale = Image.open('./scale/dpi300_alpha.tif')
        watermark = Image.open('./scale/dpi600.tif')
        width, height = base_image.size
        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        transparent.paste((mean_red, mean_green, mean_blue, 255), top_left, mask=img_original_scale)
        transparent.paste(watermark, top_left, mask=watermark)
        transparent.save('./output/' + filename, compression='tiff_jpeg', dpi=(300, 300), quality=100)

        print(filename + ' is ok! / Max_val = ' + str(max_val))


if __name__ == '__main__':
    replace_scale()

