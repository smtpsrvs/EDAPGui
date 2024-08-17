import cv2
import os

from Screen_Regions import *
from Overlay import *
from Screen import *
from Image_Templates import *
from time import sleep
import numpy as np

"""
File:Test_Routines.py    

Description:
  Class to allow testing 
"""


def main():
    # Uncomment one tests to be performed as each runs in a loop until exited.
    # Run this file instead of the main EDAPGUI file.

    # Rescale screenshots from the user scaling (i.e. 1920x1080 [0.75,0.75]
    # to the default scaling of 3440x1440 [1.0, 1.0]. Note the scaling is by
    # the ratio, not the resolution. Refer to Screen.py for resolution to
    # ratio conversions.
    # This only needs to be competed for new screenshots that were not take
    # at 3440x1440. Once complete, remove the original images and move the
    # converted images to relevant test folder.
    #
    # Does NOT require Elite Dangerous to be running.
    # ======================================================================
    rescale_screenshots('test/images-to-rescale', 0.76, 0.76)

    # Shows filtering and matching for the specified region...
    # Requires Elite Dangerous to be running.
    # ========================================================
    # template_matching_test('compass', 'compass')
    # template_matching_test('navpoint','navpoint')
    # template_matching_test('target', 'target')
    # template_matching_test('target_occluded', 'target_occluded')

    # More complicated specific test cases...
    # =======================================
    # Requires Elite Dangerous to be running.
    # compass_and_nav_test()
    # compass_test()

    # Shows regions on the Elite window...
    # Requires Elite Dangerous to be running.
    # =======================================
    # regions_test('nav_panel')
    # regions_test('disengage')

    # Testing of images...
    # The result of image matching will be placed in the 'out' folder for each image group.
    #
    # Does NOT require Elite Dangerous to be running.
    # =====================================================================================
    image_matching_test('test/target/','target', 'target')
    image_matching_test('test/compass/','compass', 'compass')
    image_matching_test('test/navpoint/','navpoint','navpoint')
    image_matching_test('test/navpoint-behind/','navpoint-behind','navpoint-behind')
    image_matching_test('test/disengage/','disengage', 'disengage')

    # HSV Tester...
    #
    # Does NOT require Elite Dangerous to be running.
    # ===============================================
    # hsv_tester("test/navpoint/Screenshot 2024-07-04 20-02-01.png")
    # hsv_tester("test/navpoint-behind/Screenshot 2024-07-04 20-01-33.png")


def draw_match_rect(img, pt1, pt2, color, thick):
    """ Utility function to add a rectangle to an image. """
    wid = pt2[0] - pt1[0]
    hgt = pt2[1] - pt1[1]

    if wid < 20:
        # cv2.rectangle(screen, pt, (pt[0] + compass_width, pt[1] + compass_height),  (0,0,255), 2)
        cv2.rectangle(img, pt1, pt2, color, thick)
    else:
        len_wid = wid / 5
        len_hgt = hgt / 5
        half_wid = wid / 2
        half_hgt = hgt / 2
        tic_len = thick - 1
        # top
        cv2.line(img, (int(pt1[0]), int(pt1[1])), (int(pt1[0] + len_wid), int(pt1[1])), color, thick)
        cv2.line(img, (int(pt1[0] + (2 * len_wid)), int(pt1[1])), (int(pt1[0] + (3 * len_wid)), int(pt1[1])), color, 1)
        cv2.line(img, (int(pt1[0] + (4 * len_wid)), int(pt1[1])), (int(pt2[0]), int(pt1[1])), color, thick)
        # top tic
        cv2.line(img, (int(pt1[0] + half_wid), int(pt1[1])), (int(pt1[0] + half_wid), int(pt1[1]) - tic_len), color,
                 thick)
        # bot
        cv2.line(img, (int(pt1[0]), int(pt2[1])), (int(pt1[0] + len_wid), int(pt2[1])), color, thick)
        cv2.line(img, (int(pt1[0] + (2 * len_wid)), int(pt2[1])), (int(pt1[0] + (3 * len_wid)), int(pt2[1])), color, 1)
        cv2.line(img, (int(pt1[0] + (4 * len_wid)), int(pt2[1])), (int(pt2[0]), int(pt2[1])), color, thick)
        # bot tic
        cv2.line(img, (int(pt1[0] + half_wid), int(pt2[1])), (int(pt1[0] + half_wid), int(pt2[1]) + tic_len), color,
                 thick)
        # left
        cv2.line(img, (int(pt1[0]), int(pt1[1])), (int(pt1[0]), int(pt1[1] + len_hgt)), color, thick)
        cv2.line(img, (int(pt1[0]), int(pt1[1] + (2 * len_hgt))), (int(pt1[0]), int(pt1[1] + (3 * len_hgt))), color, 1)
        cv2.line(img, (int(pt1[0]), int(pt1[1] + (4 * len_hgt))), (int(pt1[0]), int(pt2[1])), color, thick)
        # left tic
        cv2.line(img, (int(pt1[0]), int(pt1[1] + half_hgt)), (int(pt1[0] - tic_len), int(pt1[1] + half_hgt)), color,
                 thick)
        # right
        cv2.line(img, (int(pt2[0]), int(pt1[1])), (int(pt2[0]), int(pt1[1] + len_hgt)), color, thick)
        cv2.line(img, (int(pt2[0]), int(pt1[1] + (2 * len_hgt))), (int(pt2[0]), int(pt1[1] + (3 * len_hgt))), color, 1)
        cv2.line(img, (int(pt2[0]), int(pt1[1] + (4 * len_hgt))), (int(pt2[0]), int(pt2[1])), color, thick)
        # right tic
        cv2.line(img, (int(pt2[0]), int(pt1[1] + half_hgt)), (int(pt2[0] + tic_len), int(pt1[1] + half_hgt)), color,
                 thick)


def compass_and_nav_test():
    """ Performs a compass and nav test. """
    scr = Screen()
    templ = Image_Templates(scr.scaleX, scr.scaleY)
    scr_reg = Screen_Regions(scr, templ)

    while True:
        """ Determine the x,y offset from center of the compass of the nav point. """
        compass_region_image = scr_reg.capture_region(scr, 'compass')
        filt_compass_image, (minVal, maxVal, minLoc, maxLoc), match = (
            scr_reg.match_template_in_region('compass', 'compass'))
        pt = maxLoc

        # get wid/hgt of templates
        c_wid = scr_reg.templates.template['compass']['width']
        c_hgt = scr_reg.templates.template['compass']['height']
        wid = scr_reg.templates.template['navpoint']['width']
        hgt = scr_reg.templates.template['navpoint']['height']

        # cut out the compass from the region
        pad = 5
        compass_image = compass_region_image[abs(pt[1] - pad): pt[1] + c_hgt + pad,
                        abs(pt[0] - pad): pt[0] + c_wid + pad].copy()

        # find the nav point within the compass box
        navpt_image, (n_minVal, n_maxVal, n_minLoc, n_maxLoc), match = (
            scr_reg.match_template_in_filtered_image(compass_image, 'navpoint', 'navpoint'))
        n_pt = n_maxLoc

        # Get x and y coords of the nav point
        final_x = ((n_pt[0] + ((1 / 2) * wid)) - ((1 / 2) * c_wid)) - 5.5
        final_y = (((1 / 2) * c_hgt) - (n_pt[1] + ((1 / 2) * hgt))) + 6.5
        # must be > x to have solid hit, otherwise we are facing wrong way (empty circle)
        if n_maxVal < scr_reg.navpoint_match_thresh:
            final_z = -1.0  # Behind
        else:
            final_z = 1.0  # Ahead

        logger.debug(("maxVal=" + str(n_maxVal) + " x:" + str(final_x) + " y:" + str(final_y)))

        icompass_image_d = filt_compass_image
        draw_match_rect(icompass_image_d, pt, (pt[0] + c_wid, pt[1] + c_hgt), (0, 0, 255), 2)
        # cv2.rectangle(icompass_image_display, pt, (pt[0]+c_wid, pt[1]+c_hgt), (0, 0, 255), 2)
        # self.draw_match_rect(compass_image, n_pt, (n_pt[0] + wid, n_pt[1] + hgt), (255,255,255), 2)
        draw_match_rect(icompass_image_d, (pt[0] + n_pt[0] - pad, pt[1] + n_pt[1] - pad),
                        (pt[0] + n_pt[0] + wid - pad, pt[1] + n_pt[1] + hgt - pad), (0, 255, 0), 1)

        cv2.putText(icompass_image_d, f'Compass: {maxVal:5.2f} > {scr_reg.compass_match_thresh:5.2f}', (1, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255),
                    1, cv2.LINE_AA)
        cv2.putText(icompass_image_d, f'Nav Point: {n_maxVal:5.2f} > {scr_reg.navpoint_match_thresh:5.2f}', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                    (255, 255, 255), 1, cv2.LINE_AA)
        # cv2.circle(icompass_image_display, (pt[0]+n_pt[0], pt[1]+n_pt[1]), 5, (0, 255, 0), 3)
        cv2.imshow('compass', icompass_image_d)
        cv2.moveWindow('compass', -500, 0)

        destination_height, destination_width, _ = navpt_image.shape
        dim = (int(destination_width * 2), int(destination_height * 2))
        navpt_image = cv2.resize(navpt_image, dim, interpolation=cv2.INTER_AREA)
        cv2.putText(navpt_image, f'X:{final_x:5.2f}', (1, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1,
                    cv2.LINE_AA)
        cv2.putText(navpt_image, f'Y:{final_y:5.2f}', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1,
                    cv2.LINE_AA)
        cv2.putText(navpt_image, f'Z:{final_z:5.2f}', (1, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1,
                    cv2.LINE_AA)
        cv2.imshow('nav', navpt_image)
        cv2.moveWindow('nav', -500, 600)

        key = cv2.waitKey(10)
        if key == 27:  # ESC
            break


def compass_test():
    """ Performs a compass test. """
    scr = Screen()
    templ = Image_Templates(scr.scaleX, scr.scaleY)
    scr_reg = Screen_Regions(scr, templ)

    while True:
        region_name = 'compass'
        template = 'compass'

        img_region, (minVal, maxVal, minLoc, maxLoc), match = scr_reg.match_template_in_region(region_name, template)
        pt = maxLoc
        c_wid = scr_reg.templates.template['compass']['width']
        c_hgt = scr_reg.templates.template['compass']['height']
        draw_match_rect(img_region, pt, (pt[0] + c_wid, pt[1] + c_hgt), (0, 0, 255), 2)
        cv2.putText(img_region, f'Match: {maxVal:5.2f}', (1, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                    (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(region_name, img_region)
        cv2.imshow(template + ' match', match)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break


def template_matching_test(region_name, template):
    """ To test the template matching. Using the provided region and template.
    :param region_name: The name of the region with the required filter to apply to the image.
    :param template: The name of the template to find in each file being tested. """
    scr = Screen()
    templ = Image_Templates(scr.scaleX, scr.scaleY)
    scr_reg = Screen_Regions(scr, templ)

    while True:
        img_region, (minVal, maxVal, minLoc, maxLoc), match = scr_reg.match_template_in_region(region_name, template)
        cv2.putText(img_region, f'Match: {maxVal:5.2f}', (1, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                    (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(region_name, img_region)
        cv2.imshow(template + ' match', match)

        key = cv2.waitKey(10)
        if key == 27:  # ESC
            break


def image_matching_test(directory, region_name, template):
    """ Test all the image files in the given folder. Images are filtered using the filter defined for the region.
        The template is matched within each image and the result saved in the 'out' folder.
        :param directory: The directory to process.
        :param region_name: The name of the region with the required filter to apply to the image.
        :param template: The name of the template to find in each file being tested. """
    scr = Screen()
    templ = Image_Templates(scr.scaleX, scr.scaleY)
    scr_reg = Screen_Regions(scr, templ)

    directory_out = os.path.join(directory, 'out')
    if not os.path.exists(directory_out):
        os.makedirs(directory_out)

    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            image_out_path = os.path.join(directory_out, filename)

            image = cv2.imread(image_path)

            # Scale image to user scaling
            image = cv2.resize(image, (0, 0), fx=scr.scaleX, fy=scr.scaleY)

            img_filtered, (minVal, maxVal, minLoc, maxLoc), match = (
                scr_reg.match_template_in_filtered_image(image, region_name, template))

            pt = maxLoc
            c_wid = scr_reg.templates.template[template]['width']
            c_hgt = scr_reg.templates.template[template]['height']

            img_output = img_filtered
            img_output = image
            draw_match_rect(img_output, pt, (pt[0] + c_wid, pt[1] + c_hgt), (0, 0, 255), 2)
            cv2.putText(img_output, f'Match: {maxVal:5.2f}', (1, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                        (255, 255, 255), 1, cv2.LINE_AA)
            #cv2.imshow(template, image)
            #cv2.imshow(template + 'filtered', img_output)
            #cv2.imshow(template + ' match', match)

            cv2.imwrite(image_out_path, img_output)

            #key = cv2.waitKey(1)
            #if key == 27: # ESC
            #    break


def regions_test(region_name):
    """ Draw a rectangle indicating the given region on the Elite Dangerous window.
        :param region_name: The name of the region with the required filter to apply to the image."""
    ov = Overlay("", 1)
    scr = Screen()
    templ = Image_Templates(scr.scaleX, scr.scaleY)
    scrReg = Screen_Regions(scr, templ)

    for i, key in enumerate(scrReg.reg):
        # tgt = scrReg.capture_region_filtered(scr, key)
        # print(key)
        # print(scrReg.reg[key])
        if key == region_name:
            ov.overlay_rect(key, (scrReg.reg[key]['rect'][0],
                                  scrReg.reg[key]['rect'][1]),
                            (scrReg.reg[key]['rect'][2],
                             scrReg.reg[key]['rect'][3]), (0, 255, i * 40), 2)
            ov.overlay_paint()
    sleep(10)
    ov.overlay_quit()
    sleep(2)


def hsv_tester(image_path):
    """ Brings up a HSV test window with sliders to check the 'inRange' function on the provided image.
        Change the default values below where indicated to the values associated with the appropriate
        template in image_template.py.
        :param image_path: The file path of the image to test. """
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL) # cv2.WINDOW_AUTOSIZE)

    cv2.createTrackbar("L - H", "Trackbars", 0, 179, callback)
    cv2.createTrackbar("L - S", "Trackbars", 0, 255, callback)
    cv2.createTrackbar("L - V", "Trackbars", 0, 255, callback)
    cv2.createTrackbar("U - H", "Trackbars", 255, 179, callback)
    cv2.createTrackbar("U - S", "Trackbars", 255, 255, callback)
    cv2.createTrackbar("U - V", "Trackbars", 255, 255, callback)

    frame = cv2.imread(image_path)

    # Set default values
    cv2.setTrackbarPos("L - H", "Trackbars", 43)
    cv2.setTrackbarPos("L - S", "Trackbars", 35)
    cv2.setTrackbarPos("L - V", "Trackbars", 100)
    cv2.setTrackbarPos("U - H", "Trackbars", 100)
    cv2.setTrackbarPos("U - S", "Trackbars", 255)
    cv2.setTrackbarPos("U - V", "Trackbars", 255)

    while True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        l_h = cv2.getTrackbarPos("L - H", "Trackbars")
        l_s = cv2.getTrackbarPos("L - S", "Trackbars")
        l_v = cv2.getTrackbarPos("L - V", "Trackbars")
        u_h = cv2.getTrackbarPos("U - H", "Trackbars")
        u_s = cv2.getTrackbarPos("U - S", "Trackbars")
        u_v = cv2.getTrackbarPos("U - V", "Trackbars")

        lower_range = np.array([l_h, l_s, l_v])
        upper_range = np.array([u_h, u_s, u_v])
        mask = cv2.inRange(hsv, lower_range, upper_range)

        result = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow("original", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("result", result)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()


def rescale_screenshots(directory, scalex, scaley):
    """ Rescale all images in a folder.
    :param directory: The directory to process.
    :param scalex: The X scaling of the original image.
    :param scaley: The scaling of the original image. """

    # Calc factor to scale image up/down
    newScaleX = 1.0/scalex
    newScaleY = 1.0/scaley

    directory_out = os.path.join(directory, 'out')
    if not os.path.exists(directory_out):
        os.makedirs(directory_out)

    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            image_out_path = os.path.join(directory_out, filename)

            image = cv2.imread(image_path)

            # Scale image to user scaling
            image = cv2.resize(image, (0, 0), fx=newScaleX, fy=newScaleY)
            cv2.imwrite(image_out_path, image)


def callback(value):
    print(value)


if __name__ == "__main__":
    main()
