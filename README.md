# Segment Anything Labelling Tool (SALT)

Uses the Segment-Anything Model By Meta AI and adds a barebones interface to label images and saves the masks in the COCO format.

## Installation

1. Install [Segment Anything](https://github.com/facebookresearch/segment-anything) on any machine with a GPU. (Need not be the labelling machine).
2. Download a model checkpoint [here](https://github.com/facebookresearch/segment-anything#model-checkpoints).
3. (Optional) Install [coco-viewer](https://github.com/trsvchn/coco-viewer) to scroll through your annotations quickly.

## Usage

Run `./setup.sh [DATA DIRECTORY]` in the root directory to pre-process the images and start labeling.

There are a few keybindings that make the annotation process fast:
- Click on the object using left clicks and right click (to indicate outside object boundary) (**left** click means the pixel is inside the object, and **right** click means it's outside)
- `n` adds predicted mask into your annotations. (Add button)
- `r` rejects the predicted mask. (Reject button)
- `a` and `d` to cycle through images in your your set. (Next and Prev)
- `l` and `k` to increase and decrease the transparency of the other annotations.
- `Ctrl + S` to save progress to the COCO-style annotations file.
7. [coco-viewer](https://github.com/trsvchn/coco-viewer) to view your annotations.
    - `python cocoviewer.py -i <dataset> -a <dataset>/annotations.json`


## Detailed Usage

Please refer to **README_supplement.md**

## Demo

![How it Works Gif!](https://github.com/anuragxel/salt/raw/main/assets/how-it-works.gif)
