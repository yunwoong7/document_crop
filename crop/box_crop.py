import cv2
import numpy as np


def get_box_crop_img(img, aspect_ratio=0.8, threshold1=100, threshold2=100, cut_rate=0.8, resize_info=[]):
    """
    가장 큰 사각형을 기준으로 Crop
    :param img: (numpy.array)
    :param aspect_ratio: (float)
    :param threshold1: (int)
    :param threshold2: (int)
    :param cut_rate: (float) 이미지 기울기 보정 시 CUT 비율이 큰 경우 제외
    :param resize_info: (list)
    :return: (numpy.array)
    """
    if len(resize_info) == 4:
        resize_plus_x = resize_info[0]
        resize_plus_y = resize_info[1]
        resize_plus_w = resize_info[2]
        resize_plus_h = resize_info[3]
    else:
        resize_plus_x = 0
        resize_plus_y = 0
        resize_plus_w = 0
        resize_plus_h = 0

    logText = ""

    blur_img = cv2.GaussianBlur(img, (5, 5), 0)

    if len(img.shape) < 3:
        gray_img = blur_img
    else:
        gray_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray_img, threshold1, threshold2)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    points = []

    for h, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area >= 90:
            for p in cnt:
                points.append(p[0])

    points = np.array(points)

    if len(points) > 0:
        # aspect ratio(종횡비)가 낮은 경우 화질이 좋지 못해서
        # Cutting 영역을 잡을 수 없기 때문에 Skip 처리함
        ar = round(points[0][0] / points[0][1], 2)

        if ar < aspect_ratio:
            if points.size > 10:
                rect = cv2.minAreaRect(points)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                x, y, w, h = cv2.boundingRect(box)

                if resize_plus_x > x:
                    resize_plus_x = 0
                    x = 0
                if resize_plus_y > y:
                    resize_plus_y = 0
                    y = 0
                if resize_plus_w > w:
                    resize_plus_w = 0
                if resize_plus_h > h:
                    resize_plus_h = 0

                debug_img = cv2.rectangle(img.copy(), (x - resize_plus_x, y - resize_plus_y), (x + w + resize_plus_w, y + h + resize_plus_h), (255, 0, 0), 2)
                crop_img = img[y - resize_plus_y:y + h + resize_plus_h, x - resize_plus_x:x + w + resize_plus_w]

            img_cut_rate = (w - x) / (h - y)

            # 이미지에 잘린 비율이 큰 경우 제외(하단에 이미지가 짤리거나 흐릿한 경우 잘못 잘리는 경우 제외)
            if img_cut_rate > cut_rate:
                logText = '[INFO] Auto Crop (Skip) : ' + 'Skip (Cut Rate : ' + str(round(img_cut_rate, 2)) + ')'
                crop_img = img
            else:
                logText = '[INFO] Auto Crop : ' + 'Complete (AR( ' + str(round(ar, 2)) + ') ' + str(
                    img.shape[1]) + ', ' + str(img.shape[0]) + ' -> ' + str(crop_img.shape[1]) + ', ' + str(
                    crop_img.shape[0]) + ')'

        else:
            logText = '[INFO] Auto Crop (Skip) : ' + 'Skip (Aspect Ratio : ' + str(round(ar, 2)) + ')'

        print(logText)

        # if autocropImg.shape[2] == 4:
        #     autocropImg = autocropImg[:, :, :3]

    return crop_img