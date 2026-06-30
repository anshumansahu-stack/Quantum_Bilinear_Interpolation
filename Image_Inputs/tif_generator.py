from PIL import Image
import numpy as np

# Your image data
image_data = np.array([[1, 2], 
                       [7, 4]], dtype=np.uint8)

# Create a PIL image from the numpy array
# 'L' mode is for 8-bit grayscale
img = Image.fromarray(image_data, mode='L')

# Save as TIF
img.save("sample_2x2.tif")

print("Created sample_2x2.tif successfully.")

# To verify and load it back later:
loaded_img = Image.open("sample_2x2.tif")
loaded_arr = np.array(loaded_img)
print("Loaded Data:\n", loaded_arr)