import os
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance

year = 2020

# Path to the folder containing the images
folder_path = f'{year}-US-Counties-Images-500k/'

# Iterate over each image in the folder
for filename in tqdm(os.listdir(folder_path)):
    # Skip non-image files
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    # Get the full image path
    image_path = os.path.join(folder_path, filename)

    # Read the image
    image_org = Image.open(image_path)

    enhancer = ImageEnhance.Brightness(image_org)
    brightened_image = enhancer.enhance(1.5)  # 1.5 will increase brightness by 50%

    # Convert image to numpy array
    image = np.array(brightened_image)

    threshold = 5

    # Mask where the black pixels are (black pixels are [0, 0, 0] in RGB)
    mask = np.all(image <= threshold, axis=-1)

    # Calculate the total number of pixels in the image
    total_pixels = image.shape[0] * image.shape[1]

    # Calculate the number of black pixels
    black_pixels = np.sum(mask)

    # Calculate the percentage of black pixels
    percentage_black_pixels = (black_pixels / total_pixels) * 100

    # If the percentage of black pixels is greater than 1%, replace black pixels
    if percentage_black_pixels > 0.2 and percentage_black_pixels <= 10:
        # Impute black pixels with the mean value of the non-black pixels
        valid_pixels = image[~mask]  # Extract valid (non-black) pixels
        mean_value = np.mean(valid_pixels, axis=0)  # Calculate mean of valid pixels

        # Replace black pixels with the mean value
        image[mask] = mean_value

        # Save the modified image with the same original filename
        imputed_image = Image.fromarray(image)
        modified_image_path = os.path.join(folder_path, filename)  # Overwrite with the same name
        imputed_image.save(modified_image_path)
