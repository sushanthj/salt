WARN='\033[1;33m'
ERROR='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Get the path of the dataset directory as input
if [ $# -eq 0 ]
  then
    echo -e "${ERROR}No arguments supplied${NC}"
    echo -e "${WARN}Usage: ./setup.sh <path_to_dataset_directory>${NC}"
    exit 1
fi

# Check if the dataset directory exists
if [ ! -d "$1" ]; then
  echo -e "${ERROR}Directory $1 does not exist${NC}"
  exit 1
fi

# Check this script is run from this directory
if [ ! -f "setup.sh" ]; then
  echo -e "${ERROR}Please run this script from the directory it is in${NC}"
  exit 1
fi

# Ensure the model file is in this directory
if [ ! -f "sam_vit_h_4b8939.pth" ]; then
  echo -e "${ERROR}sam_vit_h_4b8939.pth not found in this directory${NC}"
  echo -e "${WARN}Please download the model file and place it in this directory. Or, if it is somewhere else (e.g. at /home/user/sam_vit_h_4b8939.pth), run ${NC}'ln -s /home/user/sam_vit_h_4b8939.pth .'${NC} while in this directory${NC}"
fi

# Extract the embeddings
echo -e "${NC}Extracting embeddings${NC}"
python3 helpers/extract_embeddings.py --dataset-path $1

# Generate the .onyx files
echo -e "${NC}Generating .onnx file (should be quick)${NC}"
python3 helpers/generate_onnx.py --dataset-path $1

# Get the dataset directory name (e.g. 'dataset' from '/home/user/dataset')
dataset_dir=$(basename $1)

# Symlink the dataset to this directory
if [ ! -d "$dataset_dir" ]; then
  echo -e "${NC}Symlinking the dataset${NC}"
  ln -s $1 .
fi

# Run the labeling tool
echo -e "${NC}Running the labeling tool${NC}"
python3 segment_anything_annotator.py --dataset-path=$1 --categories=stalk