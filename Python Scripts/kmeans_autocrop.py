# kmeans autocrop for use with Negatives conda environment written for Bennett Photography Collection 3.25x5.5 in. film negatives
# Jeremy.D.Moore@utk.edu 2019-08-01

# ========== Imports ===========
import argparse
from pathlib import Path

import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from sklearn.cluster import MiniBatchKMeans

import img_qc.img_qc as img_qc


# ========== Fuctions ===========
def find_contours(image_binarized):

    # find the contours in the thresholded image keeping the external one
    _, contours, hierarchy = cv2.findContours(image_binarized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def find_external_rectangle(contours, minimum_area = 450000):

    # instantiate empty rectangle with angle of 0
    rect = []
    angle = 0

    # loop over the contours individually
    for (i, contour) in enumerate(contours):
    # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(contour) < minimum_area:  # use 20000 for scrapbook pages
            continue

        # compute the rotated bounding box of the contour
        box = cv2.minAreaRect(contour)
        box = cv2.boxPoints(box)
        box = np.int0(box)

        # re-order the points in tl, tr, br, bl order
        rect = img_qc.order_points(box)

        # find the points and angle for minAreaRectangle
        (x, y), (w, h), theta = cv2.minAreaRect(contour)

        # the `cv2.minAreaRect` function returns values in the
        # range [-90, 0); as the rectangle rotates clockwise the
        # returned angle trends to 0 -- in this special case we
        # need to add 90 degrees to the angle
        if theta < -45:
            angle = -(90 + theta)

        # otherwise, just take the inverse of the angle to make
        # it positive
        else:
            angle = -theta

    return rect, angle

def get_capture_one_coordinates(rect, angle, autocrop_height, pixel_padding=0, camera_width = 8256, camera_height = 6192):

    ratio = camera_height / autocrop_height # autocrop_height is height of image being cropped

    # multiply the rectangle by the original ratio
    if rect == []:  # if rect empty then set to bounds of full image
        rect = [(0, 0), (8256, 0), (8256, 6192), (0, 6192)]
    else:  # multiply by ratio
        rect *= ratio

    # find the points we need to crop the full size original
    tl, tr, br, bl = rect
    startX = max(min(tl[0], bl[0]), 0)
    startY = max(min(tl[1], tr[1]), 0)
    endX = max(tr[0], br[0])
    endY = max(bl[1], br[1])

    # add padding
    pixel_padding = int(pixel_padding)
    startX -= pixel_padding
    startY -= pixel_padding
    endX += pixel_padding
    endY += pixel_padding

    # startX/startY to max of current value and 0 to stay inside image
    startX = max(startX, 0)
    startY = max(startY, 0)

    # endX/endY to min of current value and max width/height of image to stay inside image
    endX = min(endX, camera_width)  # NOTE: NOT USING ROTATED MAX SIZE
    endY = min(endY, camera_height)

    crop_width = endX - startX
    crop_height = endY - startY

    # get center points
    center_x = startX + (crop_width / 2)
    center_y = startY + (crop_height / 2)

    # Capture One has a weird thing where Y starts at the max value and goes DOWN to zero for some reason
    # so we need to take the camera height and SUBTRACT the center_y value to get the Capture One height value
    center_y = camera_height - center_y

    # set data for Capture One
    capture_one_data = [angle, int(center_x), int(center_y), int(crop_width), int(crop_height)]

    # make each value a string
    capture_one_data_as_str = [str(x) for x in capture_one_data]

    return capture_one_data_as_str


# ========== Classes ===========
class NegativeScan:

    def __init__(self, image_path):
        self.image_path = Path(image_path)
        self.image_cv2 = cv2.imread(str(self.image_path))


    def blur_image(self, image_cv2=None):

        if not image_cv2:
            image_cv2 = self.image_cv2

        # invert image
        image_cv2 = np.invert(image_cv2)

        # debug
        #plt.imshow(image_cv2), plt.show()

        if len(image_cv2.shape) > 2:  # NOT grayscale
            image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
            image_blurred = cv2.bilateralFilter(image_cv2, 21, 21, 21)
        else:
            image_blurred = cv2.bilateralFilter(self.image_cv2, 21, 21, 21)

        return image_blurred


    def quantize(self, image_blurred = None, number_of_clusters = 6):

        if not image_blurred:
            image_blurred = self.blur_image()

        if len(image_blurred.shape) < 3:  # image grayscale
            image_blurred = cv2.cvtColor(image_blurred, cv2.COLOR_GRAY2BGR)

        image_blurred = cv2.cvtColor(image_blurred, cv2.COLOR_BGR2LAB)
        h, w = image_blurred.shape[:2]

        reshaped_image = image_blurred.reshape((image_blurred.shape[0] * image_blurred.shape[1], 3))

        # apply k-means using the specified number of clusters and
        # then create the quantizedized reshaped based on the predictions
        clt = MiniBatchKMeans(n_clusters = number_of_clusters)
        labels = clt.fit_predict(reshaped_image)
        quantized = clt.cluster_centers_.astype("uint8")[labels]

        # reshape the feature vectors to reshapeds
        image_quantized = quantized.reshape((h, w, 3))

        # convert from L*a*b* to RGB
        image_quantized = cv2.cvtColor(image_quantized, cv2.COLOR_LAB2BGR)

        return image_quantized


    def equalize(self, image_quantized = None):
        if not image_quantized:
            image_quantized = self.quantize()
        image_gray = cv2.cvtColor(image_quantized, cv2.COLOR_BGR2GRAY)
        image_equalized = cv2.equalizeHist(image_gray)
        return image_equalized


    def threshold_kmeans(self, image_equalized = None):

        if not image_equalized:
            image_equalized = self.equalize()

        # invert image if image is positive
        # image_equalized = np.invert(image_equalized)

        # manual threshold value so EVERYTHING 1-255 -> 255
        _, image_binarized = cv2.threshold(image_equalized, 1, 255, cv2.THRESH_BINARY)

        return image_binarized


# ========== Parse Arguments ===========
# parser = argparse.ArgumentParser(description='Autocrop jpeg')
# parser.add_argument('imagepath')
# parser.add_argument('-p', '--padding', type=int, default=10)
#
# args = parser.parse_args()
# image_path = Path(args.imagepath)
# padding = args.padding


# ========== Run Program ===========
if __name__ == "__main__":


    # instantiate image
    negative_scan = NegativeScan(image_path)

    # set autocrop_height
    autocrop_height = negative_scan.image_cv2.shape[0]  # numpy arrays: height, width, channels

    # get binarized image
    threshold = negative_scan.threshold_kmeans()

    # get contours
    contours = find_contours(threshold)

    # get rect, x, y, angle
    rect, angle = find_external_rectangle(contours)

    capture_one_crop_data = get_capture_one_coordinates(rect, angle, autocrop_height)

    # AppleScript needs list as single string if calling this directly -- then get items of each paragraph
    # print("\n".join(capture_one_crop_data))
