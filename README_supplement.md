```./setup.sh /home/sush/rosbags_collated/folder_with_images_from_bagfile```

NOTE: The 'folder_with_images_from_bagfile' needs to have another folder called 'images'
present within it.


# Pipeline for Annotation Setup

1. Extract all bag files required and place them in one folder eg. ```/home/rosbags```
2. Note: If you have zip files, please unzip them beforehand
3. If you have a folder structure like:
   ```
   rosbags
    |
    ├──xyz
    |   └──bag1.bag
    |
    ├──xyz
    |   └──bag2.bag
    |
    └──xyz
        └──bag3.bag
   ```
   Then, you can leave the structure as it is, the next step will specify how to collate
4. Using above structure, run the ```collate_rosbags.py``` script present in the 'helpers' folder.
   This will collate all .bag files into another folder called ```/home/rosbags_collated```
5. Finally, run ```extract_images_ptgrey.py``` in the 'helpers' folder to extract images.
   You can specify from which topic to extract images
6. Note: You may need a ros1 installation locally to extract the images. If not, you can
   use any docker which has ros1 built and install the dependencies


## Running Annotator

1. The annotator needs segment anything model installed. (Links are present in README)
2. I find it hard to have all the dependencies installed to run the annotator, and hence
   made a docker which will use the 'sam_vit_h_4b8939.pth' file and run the segmentor
3. To use this docker simply run ```docker pull sushanthj/salt_annotator:latest```
4. Then run the ```run_annotator.sh``` bash script
5. Once inside the docker environment, to launch the annotator, run:
   ```./setup.sh /home/sush/rosbags_collated/folder_with_images_from_bagfile```

