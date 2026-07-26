import argparse
import sys
import os
import cv2
import logging
from ultralytics import YOLO

# 1. 불필요한 로그 출력 억제 (채점 시 깔끔한 출력을 위해)
logging.getLogger("ultralytics").setLevel(logging.ERROR)

def parse_args():
    p = argparse.ArgumentParser("CV assignment runner")
    p.add_argument("--input", required=True, type=str, help="path to input image")
    p.add_argument("--task", required=True, type=str, choices=["presence", "bbox"], help="task to perform")
    return p.parse_args()

def main():
    args = parse_args()
    
    # 2. 이미지 경로 확인 및 로드
    if not os.path.exists(args.input):
        print("false" if args.task == "presence" else "none")
        return 0

    img = cv2.imread(args.input)
    if img is None:
        print("false" if args.task == "presence" else "none")
        return 0

    img_h, img_w = img.shape[:2]
    image_area = img_h * img_w

    # 3. 모델 로드
    model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
    
    try:
        if os.path.exists(model_path):
            model = YOLO(model_path)
        else:
            model = YOLO('yolov8n.pt') 
    except Exception:
        print("false" if args.task == "presence" else "none")
        return 0

    # 4. 추론 (Inference)
    results = model.predict(source=img, conf=0.25, verbose=False)

    detected = False
    best_box = None
    max_conf = 0

    # 5. 결과 분석 및 필터링
    if len(results) > 0:
        for box in results[0].boxes:
            coords = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, coords)
            confidence = float(box.conf[0].cpu().numpy())
            
            w = x2 - x1
            h = y2 - y1
            box_area = w * h

            if (box_area / image_area) < 0.001: 
                continue

            if confidence > max_conf:
                max_conf = confidence
                best_box = (x1, y1, w, h)
                detected = True

    # 6. Task 별 출력
    if args.task == "presence":
        if detected:
            print("true")
        else:
            print("false")

    elif args.task == "bbox":
        if detected and best_box is not None:
            x, y, w, h = best_box
            print(f"{x},{y},{w},{h}")
        else:
            print("none")

    return 0

if __name__ == "__main__":
    sys.exit(main())