from PIL import Image
import numpy as np

def TIF_to_numpy(path):
    # Load the image
    img = Image.open(path).convert('L') # 'L' ensures grayscale

    image_array = np.array(img)

    return image_array

def numpy_to_TIF(result_2d,path):
    final_img = Image.fromarray(result_2d.astype(np.uint8), mode='L')

    # Save as TIF
    final_img.save(path)

    print("OK Thank You!")
    