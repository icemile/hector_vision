#!/usr/bin/env python
import argparse
import hazmat_detection
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import pickle
from timeit import default_timer as timer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Standalone Hazmat Detection')
    parser.add_argument('--image', metavar='IMAGE_PATH', help='Full path of the image or a debug pickle')
    parser.add_argument('template_path', metavar='TEMPLATE_PATH', help='Path to folder with sign templates')
    parser.add_argument('--debug', dest='debug', help='Whether or not to show debug information', action="store_const",
                        const=True, default=False)
    parser.add_argument('--detailed', dest='detailed',
                        help='Show the effective weight for all considered templates', action='store_const', const=True,
                        default=False)

    args = parser.parse_args()
    image_path = args.image
    if image_path is None:
        image_path = raw_input("Enter image path: ")
    if os.path.splitext(image_path)[1] == ".pickle":
        with open(image_path, 'rb') as handle:
            image = pickle.load(handle)
    else:
        image = cv2.imread(image_path)

    input_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # type: np.ndarray
    detector = hazmat_detection.HazmatSignDetector(args.template_path)
    start = timer()
    detection_result = detector.detect(input_image, debug=args.debug)  # type: hazmat_detection.DetectionResult
    end = timer()
    print((end - start) * 1000, "ms")
    debug_info = detection_result.debug_information

    plt.figure("Input Image")
    plt.imshow(input_image)

    if debug_info is not None:
        plt.figure("Debug Images")
        plt.subplot(411)
        plt.imshow(detection_result.debug_information.edge_image, "gray")
        plt.subplot(412)
        plt.imshow(detection_result.debug_information.dilated_image, "gray")
        plt.subplot(413)
        out_image = input_image.copy()
        plt.imshow(cv2.drawContours(out_image, debug_info.contours, -1, np.array([255, 0, 0]), 2))
        plt.subplot(414)
        out_image = input_image.copy()
        plt.imshow(cv2.drawContours(out_image, debug_info.filtered_contours, -1, np.array([0, 255, 0]), 2))

        rows = len(debug_info.sub_images)
        figures = (rows + 4) // 5
        for n in range(figures):
            plt.figure("Sub Images %d/%d" % (n+1, figures))
            for i in range(5):
                index = 5 * n + i
                if index >= len(debug_info.sub_images):
                    break
                plt.subplot(5, 3, 3 * i + 1)
                plt.imshow(debug_info.sub_images[index][0])
                plt.subplot(5, 3, 3 * i + 2)
                plt.imshow(debug_info.sub_images[index][1], "gray")
                plt.subplot(5, 3, 3 * i + 3)
                out_image = debug_info.sub_images[index][0].copy()
                if debug_info.sub_images[index][2] is not None:
                    cv2.drawContours(out_image, [debug_info.sub_images[index][2]], -1, np.array([255, 0, 0]), 2)
                plt.imshow(out_image)

        rows = len(debug_info.best_matches)
        figures = (rows + 4) // 5
        for n in range(figures):
            plt.figure("Matches %d/%d" % (n+1, figures))
            for i in range(5):
                index = 5 * n + i
                if index >= len(debug_info.best_matches):
                    break
                plt.subplot(5, 3, 3 * i + 1)
                plt.imshow(debug_info.best_matches[index][0])
                plt.subplot(5, 3, 3 * i + 2)
                plt.imshow(debug_info.best_matches[index][1])
                plt.subplot(5, 3, 3 * i + 3)
                if debug_info.best_matches[index][3] is None:
                    plt.title("No match")
                    continue
                plt.title("%.4f - %d - %s" % debug_info.best_matches[index][3])
                if debug_info.best_matches[index][2] is not None:
                    plt.imshow(debug_info.best_matches[index][2])

        if args.detailed:
            for match in debug_info.matches:
                plt.figure()
                rows = (len(match[2]) + 3) // 4 + 1
                plt.subplot(rows, 4, 2)
                plt.imshow(match[0])
                plt.subplot(rows, 4, 3)
                plt.imshow(match[1])
                for i in range(len(match[2])):
                    plt.subplot(rows, 4, 5 + i)
                    plt.title("%.4f - %d" % match[2][i][1:])
                    plt.imshow(match[2][i][0])

        plt.figure("Detections")
        rows = len(debug_info.detections)
        for i in range(rows):
            plt.subplot(rows, 3, 3 * i + 1)
            plt.imshow(debug_info.detections[i][0])
            plt.subplot(rows, 3, 3 * i + 2)
            plt.imshow(debug_info.detections[i][1])
            plt.subplot(rows, 3, 3 * i + 3)
            plt.title(str(debug_info.detections[i][3][0]) + " - " + str(debug_info.detections[i][3][1]))
            plt.imshow(debug_info.detections[i][2])

        plt.figure("Result")
        out_image = input_image.copy()
        for detection in detection_result.detections:
            cv2.drawContours(out_image, [detection.contour], 0, np.array([255, 0, 0]), 2)
        plt.imshow(out_image)
    else:
        plt.figure("Detections")
        rows = (len(detection_result.detections) + 2) // 3
        for i in range(rows):
            plt.subplot(rows, 3, i + 1)
            plt.title(detection_result.detections[i].sign.name)
            plt.imshow(detection_result.detections[i].sign.image)

        plt.figure("Result")
        out_image = input_image.copy()
        for detection in detection_result.detections:
            cv2.drawContours(out_image, [detection.contour], 0, np.array([255, 0, 0]), 2)
        plt.imshow(out_image)

    plt.show()