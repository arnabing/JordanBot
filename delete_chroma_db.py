import shutil
import os

# Directory path for the Chroma database
chroma_data_dir = "./chroma_db"

# Check if the directory exists
if os.path.exists(chroma_data_dir):
    # Remove the directory and its contents
    shutil.rmtree(chroma_data_dir)
    print(f"{chroma_data_dir} has been deleted.")
else:
    print(f"{chroma_data_dir} does not exist.")
