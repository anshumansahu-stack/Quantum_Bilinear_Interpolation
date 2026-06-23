from qiskit import QuantumCircuit, ClassicalRegister,QuantumRegister, transpile
from qiskit_aer import AerSimulator
import circuit_gates as cg
from qiskit.quantum_info import Statevector
import neqr_encoding as NEQR
import neqr_encoding as NE
import numpy as np


## Test for Special Adding One Operation ==========================================

# Create a 3 qubit circuit
qc = QuantumCircuit(4)

# Initialize to |0111> to test edge case
qc.x(0)
qc.x(1)
qc.x(2)



# Apply U1
qc = cg.U1(qc, [0,1,2,3])

# Simulate
from qiskit_aer import AerSimulator
from qiskit import transpile

simulator = AerSimulator(method='statevector')
qc.measure_all()
compiled = transpile(qc, simulator)
result = simulator.run(compiled, shots=1).result()
counts = result.get_counts()
print(counts)

## ================================================================================

## Test for Parallel Adder Implementation =========================================

# # Create a 12 qubit circuit
# qc = QuantumCircuit(12)

# # Initialize to |0000 0010 0010> to test edge case
# qc.x(1)
# qc.x(5)

# qc, result = cg.PA(qc, (0,1,2,3), (4,5,6,7), (8,9,10,11))

# # Add classical register only for result qubits
# cr = ClassicalRegister(len(result), name='result')
# qc.add_register(cr)

# # Measure only result qubits
# for i, qubit in enumerate(result):
#     qc.measure(qubit, cr[i])

# from qiskit_aer import AerSimulator
# from qiskit import transpile

# simulator = AerSimulator(method='statevector')
# compiled = transpile(qc, simulator)
# counts = simulator.run(compiled, shots=1).result().get_counts()
# print(counts)
## ================================================================================

## Test for Parallel Subtractor Implementation =========================================

# # Create a 12 qubit circuit
# qc = QuantumCircuit(12)
# # Larger number must be on the right, Smaller number in the middle, ancilla in the left.
# # Initialize to |0000 0000 0010> to test edge case
# qc.x(1)

# qc, result = cg.PS(qc, (0,1,2,3), (4,5,6,7), (8,9,10,11))

# # Add classical register only for result qubits
# cr = ClassicalRegister(len(result), name='result')
# qc.add_register(cr)

# # Measure only result qubits
# for i, qubit in enumerate(result):
#     qc.measure(qubit, cr[i])

# from qiskit_aer import AerSimulator
# from qiskit import transpile

# simulator = AerSimulator(method='statevector')
# compiled = transpile(qc, simulator)
# counts = simulator.run(compiled, shots=1).result().get_counts()
# print(counts)
## ================================================================================

## Test for Parallel Multiplicator Implementation =========================================

# Create a multiplier circuit for n=2
# n=4
# total_qubits=((n)*((5*n)+1))//2
# print("Total qubits allocated:", total_qubits) ##Comment
# qc = QuantumCircuit(total_qubits)

# # Initialize to |...000110> to test edge case
# qc.x(0)
# qc.x(2)
# qc.x(4)
# qc.x(5)

# X=tuple(range(0,n))
# print("X:",X) ##Comment
# Y=tuple(range(n,2*n))
# print("Y:",Y) ##Comment
# ancilla=tuple(range(2*n,total_qubits))
# print("ancilla:",ancilla) ##Comment
# qc, result = PM(qc, X, Y, ancilla)

# # Add classical register only for result qubits
# cr = ClassicalRegister(len(result), name='result')
# qc.add_register(cr)

# # Measure only result qubits
# for i, qubit in enumerate(result):
#     qc.measure(qubit, cr[i])

# from qiskit_aer import AerSimulator
# from qiskit import transpile

# simulator = AerSimulator(method='matrix_product_state')
# compiled = transpile(qc, simulator, optimization_level=0)
# counts = simulator.run(compiled, shots=1).result().get_counts()
# print(counts)

## ================================================================================

# # Test for Left shift Implementation =========================================

# # Create a Left Shift circuit for n=10
# n=10
# qc = QuantumCircuit(n)

# # Initialize to |0110110110> to test edge case
# qc.x(1)
# qc.x(2)
# qc.x(4)
# qc.x(5)
# qc.x(7)
# qc.x(8)

# number=tuple(range(0,9))
# qc = LSH(qc, number, 9)

# # Add classical register only for result qubits
# cr = ClassicalRegister(len(number), name='result')
# qc.add_register(cr)

# # Measure only result qubits
# for i, qubit in enumerate(number):
#     qc.measure(qubit, cr[i])

# from qiskit_aer import AerSimulator
# from qiskit import transpile

# simulator = AerSimulator(method='statevector')
# compiled = transpile(qc, simulator, optimization_level=0, coupling_map=None)
# counts = simulator.run(compiled, shots=1).result().get_counts()
# print(counts)

# # ================================================================================

# Test for draper Implementation =========================================

# # Create a Normal circuit for n=6
# n=6
# qc = QuantumCircuit(n)

# # Initialize to |011010> to test edge case
# qc.x(1)
# qc.x(3)
# qc.x(4)

# phi_a=tuple(range(3,6))
# b=tuple(range(0,3))
# qc.append(QFTGate(len(phi_a)), list(phi_a))
# qc = draper(qc, b, phi_a,inverse=True)
# qc.append(QFTGate(len(phi_a)).inverse(), list(phi_a))

# # Add classical register only for result qubits
# cr = ClassicalRegister(len(phi_a), name='result')
# qc.add_register(cr)

# # Measure only result qubits
# for i, qubit in enumerate(phi_a):
#     qc.measure(qubit, cr[i])

# from qiskit_aer import AerSimulator
# from qiskit import transpile

# simulator = AerSimulator(method='statevector')
# compiled = transpile(qc, simulator, optimization_level=0, coupling_map=None)
# counts = simulator.run(compiled, shots=1).result().get_counts()
# print(counts)

# ================================================================================
# # Test for Normal Divider Implementation =========================================

# qc = QuantumCircuit(24)

# # Initialize to |0000 0000 > to test edge case

# qc.x(0)
# qc.x(1)
# qc.x(2)
# qc.x(10)

# partial_remainder=tuple(range(0,6))
# divisor=tuple(range(6,12))
# quotient=tuple(range(12,15))
# ancilla=tuple(range(15,18))

# registers = {
#     'anc': [17, 16, 15],
#     'Q':   [14, 13, 12],
#     'D':   [11, 10, 9, 8, 7, 6],
#     'P':   [5, 4, 3, 2, 1, 0],
#     'R':   [5,4,3]
# }

# cg.ND(qc,partial_remainder,divisor,quotient,ancilla)
# cg.print_state(qc,"Division Result of 7/2: ",registers)

# n=18
# qc = QuantumCircuit(n)

# # Initialize to |000000010000000110> to test edge case

# qc.x(1)
# qc.x(2)
# qc.x(10)

# partial_remainder=tuple(range(0,6))
# divisor=tuple(range(6,12))
# quotient=tuple(range(12,15))
# ancilla=tuple(range(15,18))

# registers = {
#     'anc': [17, 16, 15],
#     'Q':   [14, 13, 12],
#     'D':   [11, 10, 9, 8, 7, 6],
#     'P':   [5, 4, 3, 2, 1, 0],
#     'R':   [5,4,3]
# }

# cg.ND(qc,partial_remainder,divisor,quotient,ancilla)
# cg.print_state(qc,"Division Result of 6/2: ",registers)
# # ================================================================================
## Verifying NEQR Encoding==========================================================

# test_image = np.array([
#     [1, 2],
#     [7, 4]
# ])
# color_depth=3

# qc, n_row, n_col, n_color = NN_US.quantum_nearest_neighbor_upscale(test_image)
# NN_US.verify_nn_statevector(qc,n_row,n_col,n_color)
# # ================================================================================
# # Testing Oracle Gate ==============================================
# def test_oracle(oracle_gate,image, color_depth):
#     '''
#     Test the oracle by feeding each pixel position and checking output
#     '''
    
#     height, width = image.shape
#     n_y = int(np.ceil(np.log2(height)))
#     n_x = int(np.ceil(np.log2(width)))
    
#     print("\nTesting oracle pixel by pixel:")
    
#     for r in range(height):
#         for c in range(width):
#             # Build test circuit
#             row_reg   = QuantumRegister(n_y, name='row')
#             col_reg   = QuantumRegister(n_x, name='col')
#             color_reg = QuantumRegister(color_depth, name='g')
            
#             qc = QuantumCircuit(row_reg, col_reg, color_reg)
            
#             # Initialize position to (r, c)
#             r_bin = format(r, f'0{n_y}b')
#             c_bin = format(c, f'0{n_x}b')
            
#             for i, bit in enumerate(reversed(r_bin)):
#                 if bit == '1':
#                     qc.x(row_reg[i])
#             for i, bit in enumerate(reversed(c_bin)):
#                 if bit == '1':
#                     qc.x(col_reg[i])
            
#             # Apply oracle
#             qc.append(oracle_gate, list(row_reg) + list(col_reg) + list(color_reg))
            
#             # Read statevector
#             sv = Statevector.from_instruction(qc)
#             total = qc.num_qubits
            
#             for idx, amp in enumerate(sv):
#                 if abs(amp) > 0.01:
#                     bits = format(idx, f'0{total}b')
#                     color_out = bits[:color_depth]
#                     color_val = int(color_out, 2)
#                     expected  = image[r, c]
#                     status    = '✓' if color_val == expected else '✗'
#                     print(f"  Oracle({r},{c}) → color={color_val} expected={expected} {status}")
        

# # ## Pass the required params
# # oracle_gate,lookup_table=NE.build_oracle_from_neqr()
# # color_depth=3

# # if __name__ == "__main__":
# #     image = np.array([[1, 2], [7, 4]])
# #     test_oracle(oracle_gate,image, color_depth)
# # # ================================================================================
# # # ================================================================================
# from qiskit import QuantumCircuit
# from qiskit.circuit import Qubit

# # --- OLD CIRCUIT ---
# qc = QuantumCircuit(2)

# print("--- Old Circuit Qubits ---")
# for q in qc.qubits:
#     # qc.find_bit(q).index retrieves the exact positional index
#     print(f"Index {qc.find_bit(q).index}: {q}")

# # --- NEW CIRCUIT ---
# new_qubit = Qubit()
# qc.add_bits([new_qubit])

# print("\n--- New Circuit Qubits ---")
# for q in qc.qubits:
#     print(f"Index {qc.find_bit(q).index}: {q}")

# # # ================================================================================
# ## Adding new qubits
# from qiskit import QuantumCircuit
# from qiskit.circuit import Qubit

# qc = QuantumCircuit(4)

# n = 3

# # 1. Generate a list of n independent Qubit objects
# new_qubits = [Qubit() for _ in range(n)]

# # 2. Merge them into the circuit all at once
# qc.add_bits(new_qubits)

# print("Updated qubit count:", qc.num_qubits)  # Output: 7
