#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2016 Massachusetts Institute of Technology

"""Extract images from a rosbag.
"""

import os
import argparse

import cv2

import rosbag
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

"""
Example usage:

python3 extract_images_ptgrey.py /home/sush/rosbags_collated
"""

def main():
    """Extract a folder of images from a rosbag.
    """
    parser = argparse.ArgumentParser(description="Extract images from a ROS bag.")
    parser.add_argument("rosbag_dir", type=str)
    parser.add_argument("image_topic", nargs='?', type=str, default="/camera/image_raw")

    args = parser.parse_args()

    rosbag_dir = args.rosbag_dir
    count = 0

    output_dir = os.path.join(rosbag_dir, "images")

    for bagfile in os.listdir(rosbag_dir):
        if not str(bagfile).endswith(".bag"):
            continue
        # str(bagfile)[:-4] = hacky way to drop .bag extension
        # output_dir = os.path.join(rosbag_dir, os.path.splitext(bagfile)[0], "images")
        print("Extract images from %s on topic %s into %s" % (args.image_topic,
                                                              bagfile, output_dir))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        bag_file_path = os.path.join(rosbag_dir, str(bagfile))
        print("\n bag file path is ", bag_file_path)
        bag = rosbag.Bag(bag_file_path, "r")
        bridge = CvBridge()
        for topic, msg, t in bag.read_messages(topics=[args.image_topic]):
            cv_img = bridge.imgmsg_to_cv2(msg, "bgr8")

            image_name = os.path.splitext(bagfile)[0] + "_" + str(count) + ".png"
            cv2.imwrite(os.path.join(output_dir, str(image_name)), cv_img)
            print("Wrote image %i" % count)

            count += 1

        bag.close()

if __name__ == '__main__':
    main()
