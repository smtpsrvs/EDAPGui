import cv2
from time import sleep


class OnFoot:
    def __init__(self, ed_ap):
        self.ap = ed_ap

    def have_GotoYourHangar(self, scr_reg) -> bool:
        """ Look for 'Goto my Hangar' in the range, if in this region then return true """

        threshold = 0.50
        dst_image, (minVal, maxVal, minLoc, maxLoc), match = (
            scr_reg.match_template_in_region('GotoYourHangar', 'GotoYourHangar'))

        # Determine if target is in the target region
        # print(maxVal)
        if maxVal >= threshold:
            pt = maxLoc

            destination_width = scr_reg.reg['GotoYourHangar']['width']
            destination_height = scr_reg.reg['GotoYourHangar']['height']

            width = scr_reg.templates.template['GotoYourHangar']['width']
            height = scr_reg.templates.template['GotoYourHangar']['height']

            x = pt[0]
            y = pt[1]
            h = height
            w = destination_width
            tar_image = dst_image[y:y + h, x:x + w]

            #  print("get dest, final:" + str(final_x)+ " "+str(final_y))
            #  print(destination_width, destination_height, width, height)
            #  print(maxLoc)
            print("match: " + str(maxVal))

            if self.ap.cv_view:
                dst_image_d = cv2.cvtColor(tar_image, cv2.COLOR_GRAY2RGB)
                try:
                    self.ap.draw_match_rect(dst_image_d, pt, (pt[0] + width, pt[1] + height), (0, 0, 255), 2)
                    # dim = (int(destination_width / 2), int(destination_height / 2))
                    dim = (int(w), int(h))

                    img = cv2.resize(dst_image_d, dim, interpolation=cv2.INTER_AREA)
                    cv2.putText(img, f'{maxVal:5.2f} >.54', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.imshow('GotoYourHangar', img)
                    # cv2.imshow('tt', scr_reg.templates.template['target']['image'])
                    cv2.moveWindow('GotoYourHangar', self.ap.cv_view_x + 500, self.ap.cv_view_y + 250)
                except Exception as e:
                    print("exception in have_GotoYourHangar: " + str(e))
                cv2.waitKey(30)

            self.ap.set_focus_elite_window()
            sleep(0.5)
            self.ap.keys.send('UI_Select')
            self.ap.ap_ckb('log', "Goto My Hangar")
            result = True

        else:
            result = False

        return result
