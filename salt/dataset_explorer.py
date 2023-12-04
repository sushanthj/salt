import copy
import itertools
import json
import os

import cv2
import numpy as np
from distinctipy import distinctipy
from pycocotools import mask
from simplification.cutil import simplify_coords_vwp
from termcolor import colored


def init_coco(dataset_folder, image_names, categories, coco_json_path):
    coco_json = {
        "info": {
            "description": "SAM Dataset",
            "url": "",
            "version": "1.0",
            "year": 2023,
            "contributor": "Sam",
            "date_created": "2021/07/01",
        },
        "images": [],
        "annotations": [],
        "categories": [],
    }
    for i, category in enumerate(categories):
        coco_json["categories"].append(
            {"id": i, "name": category, "supercategory": category}
        )
    for i, image_name in enumerate(image_names):
        im = cv2.imread(os.path.join(dataset_folder, image_name))
        coco_json["images"].append(
            {
                "id": i,
                "file_name": image_name,
                "width": im.shape[1],
                "height": im.shape[0],
            }
        )
    with open(coco_json_path, "w") as f:
        json.dump(coco_json, f)


def bunch_coords(coords):
    coords_trans = []
    for i in range(0, len(coords) // 2):
        coords_trans.append([coords[2 * i], coords[2 * i + 1]])
    return coords_trans


def unbunch_coords(coords):
    return list(itertools.chain(*coords))


def bounding_box_from_mask(mask):
    mask = mask.astype(np.uint8)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    all_contours = []
    for contour in contours:
        all_contours.extend(contour)
    convex_hull = cv2.convexHull(np.array(all_contours))
    x, y, w, h = cv2.boundingRect(convex_hull)
    return x, y, w, h


def parse_mask_to_coco(image_id, anno_id, image_mask, category_id, poly=False):
    start_anno_id = anno_id
    x, y, width, height = bounding_box_from_mask(image_mask)
    if poly is False:
        fortran_binary_mask = np.asfortranarray(image_mask)
        encoded_mask = mask.encode(fortran_binary_mask)
    if poly is True:
        contours, _ = cv2.findContours(image_mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    annotation = {
        "id": start_anno_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [float(x), float(y), float(width), float(height)],
        "area": float(width * height),
        "iscrowd": 0,
        "segmentation": [],
        "keypoints": [],
    }
    if poly is False:
        annotation["segmentation"] = encoded_mask
        annotation["segmentation"]["counts"] = str(
            annotation["segmentation"]["counts"], "utf-8"
        )
    if poly is True:
        for contour in contours:
            sc = simplify_coords_vwp(contour[:,0,:], 2).ravel().tolist()
            annotation["segmentation"].append(sc)
    return annotation


def parse_mask_to_coco_mode_2(image_id, anno_id, image_mask,
                              category_id, input_poitns, lane_width, poly=True):
    start_anno_id = anno_id
    x, y, width, height = bounding_box_from_mask(image_mask)
    annotation = {
        "id": start_anno_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [float(x), float(y), float(width), float(height)],
        "area": float(width * height),
        "iscrowd": 0,
        "segmentation": [],
        "keypoints": [],
    }
    # use the input points to get the contours directly as done in editor.add_click_mode_2
    for i in range(0, input_poitns.shape[0] - 1, 2):
        x1, y1 = input_poitns[i]
        x2, y2 = input_poitns[i+1]
        # Get the polygon vertices
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        polygon_vertices = [
            x1 - lane_width, y1,
            x1, y1,
            x1 + lane_width, y1,
            x2 + lane_width, y2,
            x2, y2,
            x2 - lane_width, y2,
            x1 - lane_width, y1,
        ]
        annotation["segmentation"].append(polygon_vertices)
    return annotation

def add_keypoints_to_annotation(annotation, input_points):
        """
        input_points[0] = (x1,y1)
        input_points[1] = (x2,y2)
        """
        # for every pair of (x1,y1) and (x2,y2), interpolate to find 10 points in between
        # then, add these points to the annotation
        lanes = []
        for i in range(input_points.shape[0]):
            x1, y1 = input_points[i]
            lanes.append(int(x1))
            lanes.append(int(y1))
            lanes.append(2) # x,y,visibility

        annotation["keypoints"] = lanes
        return annotation


class DatasetExplorer:
    def __init__(self, dataset_folder, categories=None, coco_json_path=None):
        self.dataset_folder = dataset_folder
        self.image_names = os.listdir(os.path.join(self.dataset_folder, "images"))
        print(colored("Labeling {} images from directory {}".format(len(self.image_names), self.dataset_folder), "green"))
        self.image_names = [
            os.path.split(name)[1]
            for name in self.image_names
            if name.endswith(".jpg") or name.endswith(".png")
        ]
        self.coco_json_path = coco_json_path
        if not os.path.exists(coco_json_path):
            self.__init_coco_json(categories)
        with open(coco_json_path, "r") as f:
            self.coco_json = json.load(f)

        self.categories = [
            category["name"] for category in self.coco_json["categories"]
        ]
        self.annotations_by_image_id = {}
        for annotation in self.coco_json["annotations"]:
            image_id = annotation["image_id"]
            if image_id not in self.annotations_by_image_id:
                self.annotations_by_image_id[image_id] = []
            self.annotations_by_image_id[image_id].append(annotation)

        # self.global_annotation_id = len(self.coco_json["annotations"])
        try:
            self.global_annotation_id = (
                max(self.coco_json["annotations"], key=lambda x: x["id"])["id"] + 1
            )
        except:
            self.global_annotation_id = 0
        self.category_colors = distinctipy.get_colors(len(self.categories), exclude_colors=[(0, 1, 0)])
        self.category_colors = [
            tuple([int(255 * c) for c in color]) for color in self.category_colors
        ]

    def __init_coco_json(self, categories):
        appended_image_names = [
            os.path.join("images", name) for name in self.image_names
        ]
        init_coco(
            self.dataset_folder, appended_image_names, categories, self.coco_json_path
        )

    def get_colors(self, category_id):
        return self.category_colors[category_id]

    def get_categories(self, get_colors=False):
        if get_colors:
            return self.categories, self.category_colors
        return self.categories

    def get_num_images(self):
        return len(self.image_names)

    def get_image_data(self, image_id):
        image_name = self.coco_json["images"][image_id]["file_name"]
        image_path = os.path.join(self.dataset_folder, image_name)
        embedding_path = os.path.join(
            self.dataset_folder,
            "embeddings",
            os.path.splitext(os.path.split(image_name)[1])[0] + ".npy",
        )
        image = cv2.imread(image_path)
        image_bgr = copy.deepcopy(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_embedding = np.load(embedding_path)
        return image, image_bgr, image_embedding

    def __add_to_our_annotation_dict(self, annotation):
        image_id = annotation["image_id"]
        if image_id not in self.annotations_by_image_id:
            self.annotations_by_image_id[image_id] = []
        self.annotations_by_image_id[image_id].append(annotation)

    def get_annotations(self, image_id, return_colors=False):
        if image_id not in self.annotations_by_image_id:
            return [], []
        cats = [a["category_id"] for a in self.annotations_by_image_id[image_id]]
        colors = [self.category_colors[c] for c in cats]
        if return_colors:
            return self.annotations_by_image_id[image_id], colors
        return self.annotations_by_image_id[image_id]

    def delete_annotations(self, image_id, annotation_id):
        for annotation in self.coco_json["annotations"]:
            if (
                annotation["image_id"] == image_id and annotation["id"] == annotation_id
            ):  # and annotation["id"] in annotation_ids:
                self.coco_json["annotations"].remove(annotation)
                break
        for annotation in self.annotations_by_image_id[image_id]:
            if annotation["id"] == annotation_id:
                self.annotations_by_image_id[image_id].remove(annotation)
                break

    def add_annotation(self, image_id, category_id, mask,
                       input_points, mode, lane_width, poly=True):
        if mask is None:
            return
        if mode == 1:
            annotation = parse_mask_to_coco(
                image_id, self.global_annotation_id, mask, category_id, poly=poly
            )
        elif mode == 2:
            annotation = parse_mask_to_coco_mode_2(
                image_id, self.global_annotation_id,
                mask, category_id, input_points, lane_width, poly=poly
            )
        self.__add_to_our_annotation_dict(annotation)
        self.coco_json["annotations"].append(annotation)
        self.global_annotation_id += 1

    def save_annotation(self):
        with open(self.coco_json_path, "w") as f:
            json.dump(self.coco_json, f)
