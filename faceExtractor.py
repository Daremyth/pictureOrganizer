# import the necessary packages
from PIL import Image
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--directory", required=True,
	help="path to input directory of images to analyze")
args = vars(ap.parse_args())

dirName = args["directory"]

listOfFiles = list()
for (dirpath, dirnames, filenames) in os.walk(dirName):
	listOfFiles += [os.path.join(dirpath, file) for file in filenames]

for file in listOfFiles:
	print("Processing {}".format(file))
	image = cv2.imread(file)
	if image is not None:
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		boxes = face_recognition.face_locations(rgb,
		model="hog")
		if len(boxes)>0:
			for box in boxes:
				top, right, bottom, left = box
				print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))
				cv2.rectangle(image, (left-100, top-100), (right+50, bottom+50), (0, 255, 0), 2)

			crop_img = image[top-50:bottom+50, left-50:right+50]
			image = ResizeWithAspectRatio(image, height=800)
			#cv2.imshow("Image", image)
			
			cv2.imshow("Image", crop_img)
			cv2.waitKey(0)