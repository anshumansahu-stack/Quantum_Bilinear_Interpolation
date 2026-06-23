import numpy as np

def classical_bilinear_wrapped(image, new_shape):
    old_h, old_w = image.shape
    new_h, new_w = new_shape
    output = np.zeros((new_h, new_w), dtype=float)

    # Calculate n (original bits) and m (fractional bits)
    n_y = int(np.ceil(np.log2(old_h)))
    n_x = int(np.ceil(np.log2(old_w)))
    
    # m is the number of 'expansion' bits
    m_y = int(np.ceil(np.log2(new_h))) - n_y
    m_x = int(np.ceil(np.log2(new_w))) - n_x
    
    scale_y = 2**m_y
    scale_x = 2**m_x

    for y_p in range(new_h):
        for x_p in range(new_w):
            # 1. Base coordinates (The 'n' qubits: row, col)
            # We use modulo to simulate the quantum register wrapping
            y = (y_p >> m_y) % old_h
            x = (x_p >> m_x) % old_w
            
            # 2. Fractional bits (The 'm' qubits: e_row, e_col)
            # These are the bits below the n-qubit threshold
            h_bit = y_p & (scale_y - 1)
            w_bit = x_p & (scale_x - 1)

            # 3. Neighbors with WRAPPING (U1 Modular logic)
            y0, y1 = y, (y + 1) % old_h
            x0, x1 = x, (x + 1) % old_w

            # 4. Integer Weights (Scale - fractional_bits)
            wy0, wy1 = (scale_y - h_bit), h_bit
            wx0, wx1 = (scale_x - w_bit), w_bit

            # 5. Weighted Summation
            total_sum = (
                (wy0 * wx0 * image[y0, x0]) + 
                (wy1 * wx0 * image[y1, x0]) + 
                (wy0 * wx1 * image[y0, x1]) + 
                (wy1 * wx1 * image[y1, x1])
            )
            
            # 6. Normal Division (ND Gate)
            # Dividing by the product of scales (Total weighted area)
            output[y_p, x_p] = total_sum // (scale_y * scale_x)

    return output

# Test with 2x2 -> 8x8 (m will be 2)
image = np.array([[1, 2], [7, 4]])
res = classical_bilinear_wrapped(image, (8, 8))
print("Generalised Wrapping Result:")
print(res)