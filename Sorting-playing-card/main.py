import argparse
import cv2
import numpy as np
import sys
import os

RANK_FILENAMES = {
    'A': 'Ace', '2': 'Two', '3': 'Three', '4': 'Four', '5': 'Five',
    '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Nine', '10': 'Ten',
    'J': 'Jack', 'Q': 'Queen', 'K': 'King'
}

SUIT_FILENAMES = {
    'C': 'Clubs', 'D': 'Diamonds', 'H': 'Hearts', 'S': 'Spades'
}

RANK_ORDER = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
    '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
}
SUIT_ORDER = {'C': 0, 'D': 1, 'H': 2, 'S': 3}

CARD_WIDTH = 400
CARD_HEIGHT = 600

RANK_ROI_TOP    = 0.02
RANK_ROI_BOTTOM = 0.29
RANK_ROI_WIDTH  = 0.15

SUIT_ROI_TOP    = 0.13
SUIT_ROI_BOTTOM = 0.26
SUIT_ROI_WIDTH  = 0.15

def parse_args():
    p = argparse.ArgumentParser("CV assignment runner")
    p.add_argument("--input", required=True, type=str, help="path to input image")
    return p.parse_args()

def sort_points(points):
    points = points.astype(np.float32)
    new_points = np.zeros((4, 2), dtype="float32")
    s = points.sum(axis=1)
    new_points[0] = points[np.argmin(s)]
    new_points[2] = points[np.argmax(s)]
    diff = np.diff(points, axis=1)
    new_points[1] = points[np.argmin(diff)]
    new_points[3] = points[np.argmax(diff)]
    return new_points

def four_point_transform(image, pts):
    rect = sort_points(pts)
    dst = np.array([
        [0, 0],
        [CARD_WIDTH - 1, 0],
        [CARD_WIDTH - 1, CARD_HEIGHT - 1],
        [0, CARD_HEIGHT - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (CARD_WIDTH, CARD_HEIGHT))

def load_templates(folder_path='Card_Imgs'):
    rank_temps = {}
    suit_temps = {}
    for key, filename in RANK_FILENAMES.items():
        path = os.path.join(folder_path, filename + '.jpg')
        if not os.path.exists(path): path = os.path.join(folder_path, filename + '.png')
        if os.path.exists(path): rank_temps[key] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    for key, filename in SUIT_FILENAMES.items():
        path = os.path.join(folder_path, filename + '.jpg')
        if not os.path.exists(path): path = os.path.join(folder_path, filename + '.png')
        if os.path.exists(path): suit_temps[key] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return rank_temps, suit_temps

def match_template(roi_gray, templates):
    best_key = None
    best_score = -1
    for key, temp_img in templates.items():
        t_h, t_w = temp_img.shape[:2]
        r_h, r_w = roi_gray.shape[:2]
        if t_h > r_h or t_w > r_w: continue
        res = cv2.matchTemplate(roi_gray, temp_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_score:
            best_score = max_val
            best_key = key
    return best_key, best_score

# main 함수
def main():
    args = parse_args()
    
    img_color = cv2.imread(args.input)
    if img_color is None:
        print("Error: Image not found.")
        return

    rank_templates, suit_templates = load_templates('Card_Imgs')
    if not rank_templates or not suit_templates:
        print("Error: Templates not found.")
        return

    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0) 
    ret, img_binary = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_cards = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 5000: 
            continue

        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            if not cv2.isContourConvex(approx):
                continue
            
            pts = approx.reshape(4, 2)
            
            card_img = four_point_transform(img_color, pts)
            card_gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
            
            H, W = card_gray.shape
            
            r_y1 = int(H * RANK_ROI_TOP)
            r_y2 = int(H * RANK_ROI_BOTTOM)
            r_x2 = int(W * RANK_ROI_WIDTH)
            rank_roi = card_gray[r_y1:r_y2, 0:r_x2]

            s_y1 = int(H * SUIT_ROI_TOP)
            s_y2 = int(H * SUIT_ROI_BOTTOM)
            s_x2 = int(W * SUIT_ROI_WIDTH)
            suit_roi = card_gray[s_y1:s_y2, 0:s_x2]

            _, rank_thresh = cv2.threshold(rank_roi, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            _, suit_thresh = cv2.threshold(suit_roi, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            rank_key, rank_score = match_template(rank_thresh, rank_templates)
            suit_key, suit_score = match_template(suit_thresh, suit_templates)

            if (rank_key is not None and suit_key is not None and rank_score >= 0.3 and suit_score >= 0.0):
                detected_cards.append({'rank': rank_key, 'suit': suit_key})

    detected_cards.sort(key=lambda x: (RANK_ORDER[x['rank']], SUIT_ORDER[x['suit']]))

    output_list = []
    for card in detected_cards:
        card_str = f"{card['suit']}{card['rank']}"
        output_list.append(card_str)

    print(" ".join(output_list))
    return 0

if __name__ == "__main__":
    sys.exit(main())

#python main.py --input test_card23.jpg
#python debug.py test_card23.jpg