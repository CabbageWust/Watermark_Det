import glob
import os
import cv2

video_path = './data/video5000/*'
dst_path = './backgrounds'
if not os.path.exists(dst_path):
    os.mkdir(dst_path)
video_list = glob.glob(video_path)

c = 0
tt = 0
for i, file in  enumerate(video_list):
    tt += 1
    if tt < 3000:
        continue
    cap = cv2.VideoCapture(file)
    count = 0
    num = 0
    print(i)
    while (cap.isOpened()):
        ret, frame = cap.read()
        count += 1

        if ret == False or num > 0:
            break

        if count % 40 == 0:
            # name = str(i) + '_' + str(num) + '_0821qmk' + '.jpg'
            name = str(tt) + '.jpg'
            savename = os.path.join(dst_path, name)
            h, w = frame.shape[:2]
            # savepic = frame[:h//8, w//2:, :]
            if h > w:
                cv2.imwrite(savename, frame)
                c += 1
            num += 1
