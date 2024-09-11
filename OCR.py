import cv2
import numpy as np
from paddleocr import PaddleOCR

"""
File:OCR.py    

Description:
  Class for OCR processing using PaddleOCR. 

Author: Stumpii
"""


def get_selected_item_image(image, min_w, min_h):
    """ Attempts to find a selected item in an image. The selected item is identified by being solid orange or blue
    rectangle with dark text, instead of orange/blue text on a dark background.
    The image of the first item matching the criteria and minimum width and height is returned, otherwise None.
    """
    # Perform HSV mask
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_range = np.array([0, 0, 180])
    upper_range = np.array([255, 255, 255])
    mask = cv2.inRange(hsv, lower_range, upper_range)
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    # cv2.imwrite('test/nav-panel/out/masked.png', masked_image)

    # Convert to gray scale and invert
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('test/nav-panel/out/gray.png', gray)

    # Convert to B&W to allow FindContours to find rectangles.
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)  # | cv2.THRESH_BINARY_INV)
    # cv2.imwrite('test/nav-panel/out/thresh1.png', thresh1)

    # Finding contours in B&W image. White are the areas detected
    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cropped = image
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # The whole row will be wider than random matching elements.
        if w > min_w and h > min_h:
            # Drawing a rectangle on the copied image
            # rect = cv2.rectangle(crop, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Crop to leave only the contour (the selected rectangle)
            cropped = image[y:y + h, x:x + w]

            # cv2.imshow("cropped", cropped)
            return cropped

    # No good matches, then return None
    return None


class OCR:
    def __init__(self):
        self.paddleocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False, use_dilation=True,
                                   use_space_char=True)

    def image_ocr_no_filter(self, image):
        """ Perform OCR with no filtering. Returns the full OCR data and a simplified list of strings.
        This routine is the slower than the simplified OCR.

        OCR Data is returned in the following format, or (None, None):
        [[[[[86.0, 8.0], [208.0, 8.0], [208.0, 34.0], [86.0, 34.0]], ('ROBIGO 1 A', 0.9815958738327026)]]]
        """
        ocr_data = self.paddleocr.ocr(image)

        print(ocr_data)

        # ocr_textlist = []
        # for bbox, text, score in ocr_data:
        #     if score > 0.25:
        #         ocr_textlist.append(text)

        # Annotate the image with the OCR results
        # for res in ocr_data:
        #     for line in res:
        #         points = np.array(line[0]).astype(np.int32)
        #         w = points[1][0] - points[0][0]

        if ocr_data is None:
            return None, None
        else:
            ocr_textlist = []
            for res in ocr_data:
                for line in res:
                    ocr_textlist.append(line[1][0])

            return ocr_data, ocr_textlist

    def image_simple_ocr_no_filter(self, image):
        """ Perform OCR with no filtering. Returns a simplified list of strings with no positional data.
        This routine is faster than the function that returns the full data.

        OCR Data is returned in the following format, or None:
        [[[[[86.0, 8.0], [208.0, 8.0], [208.0, 34.0], [86.0, 34.0]], ('ROBIGO 1 A', 0.9815958738327026)]]]
        """
        ocr_data = self.paddleocr.ocr(image)

        print(ocr_data)

        if ocr_data is None:
            return None
        else:
            ocr_textlist = []
            for res in ocr_data:
                for line in res:
                    ocr_textlist.append(line[1][0])

            return ocr_textlist

    def get_selected_item_data(self, image, min_w, min_h):
        """ Attempts to find a selected item in an image. The selected item is identified by being solid orange or blue
            rectangle with dark text, instead of orange/blue text on a dark background.
            The OCR daya of the first item matching the criteria is returned, otherwise None.
            @param image: The image to check.
            @param min_w: The minimum width of the text block.
            @param min_h: The minimum height of the text block.
        """
        # Find the selected item/menu (solid orange)
        img_selected = get_selected_item_image(image, min_w, min_h)
        if img_selected is not None:
            # cv2.imshow("img", img_selected)

            #crop_with_border = cv2.copyMakeBorder(img_selected, 40, 20, 20, 20, cv2.BORDER_CONSTANT)
            ocr_data, ocr_textlist = self.ocr.image_ocr_no_filter(img_selected)

            #draw_bounding_boxes(crop_with_border, ocr_data, 0.25)
            #cv2.imwrite(image_out_path, crop_with_border)
            #draw_bounding_boxes(crop_with_border, ocr_data, 0.25)
            #cv2.imwrite(image_out_path, crop_with_border)
            #cv2.imshow("ocr", crop_with_border)
            if ocr_data is not None:
                return img_selected, ocr_data, ocr_textlist
            else:
                return None, None, None

        else:
            return None, None, None


