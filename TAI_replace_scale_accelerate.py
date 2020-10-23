import cv2
import numpy as np
from PIL import Image
import glob
import timeit
import os
import threading


def replace_scale_thread1():
    folder_index = 0
    for folder in folderlist:
        print('Start! - ' + folder + ' - thread1')
        for filename in all_file[folder_index][::2]:
            replace_scale(filenames=filename, folders=folder)
        folder_index = folder_index + 1


def replace_scale_thread2():
    folder_index = 0
    for folder in folderlist:
        print('Start! - ' + folder + ' - thread2')
        for filename in all_file[folder_index][1::2]:
            replace_scale(filenames=filename, folders=folder)
        folder_index = folder_index + 1


def make_dir():
    folder_index = 0
    for folder in folderlist:
        all_file.append(glob.glob('./' + InputPath + '/' + folder + '/*.tif'))

        if len(all_file[folder_index]) == 0:
            print(folder + 'no file!\n')
        else:
            os.makedirs(SavePath + '/' + folder, exist_ok=True)

        folder_index = folder_index + 1


def replace_scale(filenames, folders):
    try:
        lock.acquire()
        start = timeit.default_timer()
        img_original = cv2.imdecode(np.fromfile(filenames, dtype='uint8'), 1)
        lock.release()
        img_original_gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
        # img_original_gray_dn = cv2.fastNlMeansDenoising(img_original_gray, None, 20, 5, 15)
        scale_original = cv2.imread('./scale/dpi300.tif', 0)

        lock.acquire()
        res = cv2.matchTemplate(img_original_gray, scale_original, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_point, max_point = cv2.minMaxLoc(res)
        top_left = max_point
        lock.release()

        if max_val < 0.5:
            lock.acquire()
            with open('val_lower_than_0point8.txt', mode='a') as F:
                F.write(os.path.basename(filenames) + ' Max_val = ' + str(max_val) + ' / Path: ' + Family_folder + '/' + folders + '\n')
            lock.release()

        if max_val >= 0.5:
            rgb_size = 30
            rgb_values = img_original[top_left[1] - rgb_size:top_left[1], top_left[0]:top_left[0] + rgb_size]

            mean_blue = int(np.round(np.mean(rgb_values[:, :, 0])))
            mean_green = int(np.round(np.mean(rgb_values[:, :, 1])))
            mean_red = int(np.round(np.mean(rgb_values[:, :, 2])))

            with Image.open(filenames) as base_image, Image.open(
                    './scale/dpi300_alpha.tif') as scale_original_4c, Image.open('./scale/dpi600.tif') as watermark:
                width, height = base_image.size
                transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                transparent.paste(base_image, (0, 0))
                transparent.paste((mean_red, mean_green, mean_blue, 255), top_left, mask=scale_original_4c)
                transparent.paste(watermark, top_left, mask=watermark)
                transparent.save(SavePath + '/' + folders + '/' + os.path.basename(filenames), compression='tiff_jpeg', quality=100, dpi=(300, 300))

        del img_original
        del img_original_gray
        del scale_original

        stop = timeit.default_timer()

        print(os.path.basename(filenames) + ' is ok! / Max_val = ' + str(max_val) + ' / time : ' + str(stop - start))

    except Exception:
        lock.release()
        lock.acquire()
        print('error in %s' % os.path.basename(filenames))
        with open('error.txt', mode='a') as F:
            F.write('error in %s/%s/%s\n' % (InputPath, folders, os.path.basename(filenames)))
        lock.release()


if __name__ == '__main__':
    InputPath = input('Input Path=?\n')
    Family_folder = input('Family Folder=?\n')
    SavePath = input('Img Save Path=?\n')
    folderlist = os.listdir(InputPath)
    all_file = list()
    make_dir()
    lock = threading.Lock()
    t1 = threading.Thread(target=replace_scale_thread1)
    t2 = threading.Thread(target=replace_scale_thread2)

    start_time = timeit.default_timer()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    end_time = timeit.default_timer()
    exit_program = input('time: ' + str(end_time-start_time) + '\npress enter to quit')
