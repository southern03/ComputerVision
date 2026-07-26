import argparse
import cv2
import sys
import numpy as np

def parse_args():
    p = argparse.ArgumentParser("CV assignment runner")
    p.add_argument("--input", required=True, type=str, help="path to input image")
    return p.parse_args()

def classify_coin(img, circles):
    coin_counts = {500: 0, 100: 0, 50: 0, 10: 0}
    total_sum = 0

    if circles is None or len(circles[0]) == 0:
        return coin_counts, total_sum

    circles = np.uint16(np.around(circles))[0]
    
    # 구리색 마스크
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_color = np.array([5, 30, 30])
    upper_color = np.array([45, 255, 255])
    mask = cv2.inRange(hsv_img, lower_color, upper_color)

    # 동전 분류
    radii = [c[2] for c in circles]
    unique_radii = sorted(list(set(radii)), reverse=True)

    TOLERANCE_RATIO = 0.05
    
    radius_groups = []
    if unique_radii:
        current_group = [unique_radii[0]]
        for r in unique_radii[1:]:
            group_avg = np.mean(current_group)
            if r > group_avg * (1 - TOLERANCE_RATIO):
                current_group.append(r)
            else:
                radius_groups.append(current_group)
                current_group = [r]
        radius_groups.append(current_group)

    # 그룹에 동전 액면가 설정
    coin_values = [500, 100, 50, 10]
    
    mapping = {}
    for i, group in enumerate(radius_groups):
        if i < len(coin_values):
            mapping[np.mean(group)] = coin_values[i]
        else:
            break

    # 검출된 원 개수 카운트
    for (x, y, r) in circles:
        sample_radius = max(5, int(r * 0.2)) 
        try:
            mask_area = mask[max(0, y - sample_radius):min(img.shape[0], y + sample_radius),
                             max(0, x - sample_radius):min(img.shape[1], x + sample_radius)]
            mask_mean = np.mean(mask_area)
        except:
            mask_mean = 0

        is_10_won = False
        if mask_mean > 120:
            if len(radius_groups) >= 4 and r < np.mean(radius_groups[3]) * 1.1:
                is_10_won = True
            elif len(radius_groups) < 4 and r < np.mean(radius_groups[-1]) * 1.1:
                is_10_won = True
        
        if is_10_won:
            coin_counts[10] += 1
            total_sum += 10
            continue
        
        # 크기 분류
        classified = False
        min_diff = float('inf')
        assigned_value = None
        
        for avg_r, value in mapping.items():
            if value == 10:
                continue
                
            diff = abs(r - avg_r)
            if diff < min_diff:
                min_diff = diff
                assigned_value = value
                
        if assigned_value is not None and min_diff / r < 0.05:
            coin_counts[assigned_value] += 1
            total_sum += assigned_value
            classified = True
                
    return coin_counts, total_sum


def main():
    args = parse_args()
    img = cv2.imread(args.input)

    if img is None:
        print(f"Error: Could not read image at {args.input}", file=sys.stderr) 
        return 1

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 2) 

    h, w = gray.shape[:2]
    scale = min(h, w)

    minDist = int(scale * 0.2) 
    minRadius = int(scale * 0.03) 
    maxRadius = int(scale * 0.5)  

    # 원 검출
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,          
        minDist=minDist,    
        param1=180,      
        param2=35,  
        minRadius=minRadius,    
        maxRadius=maxRadius    
    )

    # 동전 분류, 합계 계산
    coin_counts, total_sum = classify_coin(img, circles)

    print(f"500:{coin_counts[500]}")
    print(f"100:{coin_counts[100]}")
    print(f"50:{coin_counts[50]}")
    print(f"10:{coin_counts[10]}")
    print(f"{total_sum}")

    return 0

if __name__ == "__main__":
    sys.exit(main())