import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

def prepare_circuit(image: np.ndarray, color_depth: int = 2) -> QuantumCircuit:
    """
    Prepares a NEQR (Novel Enhanced Quantum Representation) circuit for a given 2D image.
    
    Args:
        image: A 2D numpy array representing the image. Dimensions must be powers of 2.
        color_depth: The number of qubits used to represent the color of a pixel (q).
        
    Returns:
        QuantumCircuit: The circuit that prepares the NEQR state.
    """
    # Image dimensions (assumes square image of size 2^n x 2^n for simplicity in this implementation)
    height, width = image.shape
    
    # Calculate required qubits
    n_y = int(np.ceil(np.log2(height)))
    n_x = int(np.ceil(np.log2(width)))
    
    # Registers
    pixel_reg = QuantumRegister(color_depth, name='g')
    y_reg = QuantumRegister(n_y, name='row')
    x_reg = QuantumRegister(n_x, name='col')
    
    # Complete circuit
    qc = QuantumCircuit(x_reg, y_reg, pixel_reg)
    
    # 1. Put position qubits in superposition
    qc.h(y_reg)
    qc.h(x_reg)
    qc.barrier()
    
    # 2. Encode the pixel values
    for y in range(height):
        for x in range(width):
            pixel_value = int(image[y, x])
            
            # Skip if pixel value is 0 (as qubits are initialized to 0)
            if pixel_value == 0:
                continue
                
            # Convert y and x to binary strings for control matching
            # Format: zfill pads with zeros to the left. Qiskit little-endian means 
            # the 0th qubit is the rightmost bit in the string.
            y_bin = format(y, f'0{n_y}b')
            x_bin = format(x, f'0{n_x}b')
            
            # Combine condition: list of control states (0 or 1)
            # We want to activate when y_reg matches y_bin and x_reg matches x_bin
            # Note: qiskit bit strings are read right-to-left for qubit index 0->n
            # so the MSB is at index -1, LSB is at index 0.
            
            # We apply X gates to coordinate qubits where the binary representation has a '0'
            # to make the multi-controlled gate trigger on the '0' state.
            
            # Apply X gates for zero-controls
            for i, bit in enumerate(reversed(y_bin)):
                if bit == '0':
                    qc.x(y_reg[i])
                    
            for i, bit in enumerate(reversed(x_bin)):
                if bit == '0':
                    qc.x(x_reg[i])
                    
            # Apply the multi-controlled X gate to set the pixel value
            pixel_bin = format(pixel_value, f'0{color_depth}b')
            control_qubits = list(y_reg) + list(x_reg)
            
            for i, bit in enumerate(reversed(pixel_bin)):
                if bit == '1':
                    qc.mcx(control_qubits, pixel_reg[i])
                    
            # Undo X gates for zero-controls (uncompute)
            for i, bit in enumerate(reversed(y_bin)):
                if bit == '0':
                    qc.x(y_reg[i])
                    
            for i, bit in enumerate(reversed(x_bin)):
                if bit == '0':
                    qc.x(x_reg[i])
                    
            qc.barrier()
            
    return qc

def draw_circuit(test_image,color_depth,circuit):
    print("Test Image (2x2):")
    print(test_image)
    
    print("\nNEQR Circuit Depth:", circuit.depth())
    print("\nNEQR Circuit:")
    print(circuit.draw(output='text', filename=None, initial_state=False, cregbundle=True))
    
def verify_statevector(test_image,color_depth,circuit):

    sv = Statevector.from_instruction(circuit)
    total = circuit.num_qubits  # = 5 (3 color + 1 row + 1 col)

    print("\nNEQR State:")
    for idx, amp in enumerate(sv):
        if abs(amp) > 0.01:
            bits = format(idx, f'0{total}b')
            col   = bits[total-1]
            row   = bits[total-2]
            color = bits[:total-2]
            print(f"|color={color}⟩|row={row}⟩|col={col}⟩  amp={amp:.3f}")

def build_oracle_from_neqr(neqr_qc, shape, color_depth):
    n_y = int(np.ceil(np.log2(shape[0])))
    n_x = int(np.ceil(np.log2(shape[1])))
    sv = Statevector.from_instruction(neqr_qc)
    total = neqr_qc.num_qubits
    
    lookup_table = {}
    for idx, amp in enumerate(sv):
        if abs(amp) > 0.01:
            bits = format(idx, f'0{total}b')
            # MSB-first string: [Color (depth)][Row (n_y)][Col (n_x)]
            # We extract them and reverse to get LSB-first strings for the loop
            c_str = bits[:color_depth][::-1] 
            r_str = bits[color_depth : color_depth + n_y][::-1]
            x_str = bits[color_depth + n_y : ][::-1]
            lookup_table[(r_str, x_str)] = c_str
    
    row_reg, col_reg = QuantumRegister(n_y, 'row'), QuantumRegister(n_x, 'col')
    color_reg = QuantumRegister(color_depth, 'g')
    qc = QuantumCircuit(row_reg, col_reg, color_reg, name='Oracle')

    for (r_val, c_val), g_val in lookup_table.items():
        # r_val[0] is 2^0, maps to row_reg[0]
        for i, bit in enumerate(r_val):
            if bit == '0': qc.x(row_reg[i])
        for i, bit in enumerate(c_val):
            if bit == '0': qc.x(col_reg[i])
        
        controls = list(row_reg) + list(col_reg)
        for i, bit in enumerate(g_val):
            if bit == '1': qc.mcx(controls, color_reg[i])
            
        # Uncompute
        for i, bit in enumerate(r_val):
            if bit == '0': qc.x(row_reg[i])
        for i, bit in enumerate(c_val):
            if bit == '0': qc.x(col_reg[i])
        qc.barrier()
    return qc.to_instruction(), lookup_table