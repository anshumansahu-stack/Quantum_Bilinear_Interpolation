import numpy as np
from qiskit import QuantumCircuit
import importlib
cg=importlib.import_module("3_circuit_gates")
cm=importlib.import_module("4_circuit_methods")
NE=importlib.import_module("6_neqr_encoding")

## Row and Column labels must be Swapped!   ERROR UNRESOLVED
image = np.array([[1, 2], [7, 4]])
gray_value = 3
old_shape = (2,2)
new_shape = (4,4)

# Storing the image in NEQR and then extracting the image from the same
qc = NE.prepare_circuit(image, gray_value)
oracle_gate, lookup_table = NE.build_oracle_from_neqr(qc, image.shape, gray_value)

result_matrix = np.zeros(new_shape[0] * new_shape[1])  ## 1d array, store values
# Work area + final storage

def build_circuit(original_shape, new_shape, gray_value, oracle_gate):

    n = int(np.ceil(np.log2(image.shape[1])))
    m = int(np.ceil(np.log2(new_shape[1]))) - n
    # max_width = 7  ## For testingm[0,1;2,0] Only, Hardcoded value

    max_width = gray_value + (2 * m) + 2
    # print("max width=",max_width)

    total_qubits = (
        (5 * max_width**2) + (16 * max_width) + 4 * n + 2 * m +2*20
    )  # max_width extra for initialising value 2^2m for division at last, then required-4*n+n
    reset_per_calculation = (5 * max_width**2) + (4 * max_width) + 2 * n +2*20

    col = int(np.ceil(np.log2(original_shape[1])))  ## 1
    row = int(np.ceil(np.log2(original_shape[0])))  ## 1
    e_col = int(np.ceil(np.log2(new_shape[1]))) - col  ## 1
    e_row = int(np.ceil(np.log2(new_shape[0]))) - row  ## 1

    coord_qubits = row + e_row + col + e_col  # 4

    qubit_tuple = tuple(range(total_qubits))

    coord_qubit_tuple = qubit_tuple[:coord_qubits]

    iterations = new_shape[0] * new_shape[1]  # Total number of times the loop is run

    for i in range(0,1):  ## Just for testing purposes, only one iteration
        qc = QuantumCircuit(total_qubits)

        bin_current = f"{i:0{coord_qubits}b}"  ## Binary value denoting the current position in the expanded array

        for index, bit in enumerate(bin_current[::-1]):
            if bit == "1":
                qc.x(index)  ## For each 1 in the binary index a NOT gate is applied.
        
        # print("Current state we're working with:")
        # cm.get_local_statevector(qc,coord_qubit_tuple)

        addition_storage = qubit_tuple[
            coord_qubits
            + reset_per_calculation : coord_qubits
            + reset_per_calculation
            + (4 * max_width)
        ]
        for j in range(1):  ## Change to 4 after test

            extra_qubits = coord_qubits + max_width  # 7
            curr_qubits = len(coord_qubit_tuple) + extra_qubits
            curr_tuple = qubit_tuple[:curr_qubits]  # (0,10)

            e_col_tuple = curr_tuple[:e_col]
            col_tuple = curr_tuple[e_col : e_col + col]
            e_row_tuple = curr_tuple[e_col + col : e_col + col + e_row]
            row_tuple = curr_tuple[
                e_col + col + e_row : e_col + col + e_row + row
            ]  ## Sources

            e_source = e_col_tuple + e_row_tuple
            source = col_tuple + row_tuple

            parent_dest_index = curr_tuple[coord_qubits + len(e_source) + max_width :]
            # 2. Identify the Color bits (The 3 qubits)
            color_index_tuple = curr_tuple[
                coord_qubits + len(e_source) : coord_qubits + len(e_source) + max_width
            ]
            gray_value_tuple = color_index_tuple[:gray_value]  ## Input to the oracle

            # 3. Mapping: Copy Global bits into Parent/Dest bits
            e_dest_index = curr_tuple[
                coord_qubits : coord_qubits + len(e_source)
            ]  ##Index containing the extra qubits copied

            ## e_source= e_row+e_col
            cm.multiply_cx(qc, e_source, e_dest_index)  # Map expansion bits
            cm.multiply_cx(qc, source, parent_dest_index)  # Map parent coordinate bits

            ## Applying Addition+1 operations
            col_dest = parent_dest_index[:col]
            row_dest = parent_dest_index[col:]
            if j == 1:
                cg.U1(qc, row_dest)
            if j == 2:
                cg.U1(qc, col_dest)
            if j == 3:
                cg.U1(qc, row_dest)
                cg.U1(qc, col_dest)
            # 4. Fire the Oracle
            oracle_input_index = list(row_dest + col_dest + gray_value_tuple)
            qc.append(oracle_gate, oracle_input_index)

            cm.save_circuit_snapshot(qc,i)
            
            # print("Current color:")
            # cm.get_local_statevector(qc,color_index_tuple)

            ## To avoid the integer overflow in the circuit, gray_value number of qubits each are needed for Parallel Subtraction.
            ## I am making separate values of row and column just in case the target image dimensions are not equal.
            ## It is also not necessary that the gray qubits will be more than that of the rows and column qubits. ## SETBACK, as of now i have assumed gray_values is more.

            PS_ext_row = max_width - e_row  ##2
            PS_ext_col = max_width - e_col  ##2
            ## Adding extra bits for Parallel Subtraction
            ## n=gray value here, for each Parallel Subtraction operation n ancillary qubits are required.
            ## Total qubits entering for parallel Subtraction: PS_ext_row+PS_ext_col+(2*gray_value)+2*gray value in which the values 2^m will be initialised

            PS_extra = PS_ext_row + PS_ext_col + (4 * max_width)  ## 16
            old_size = len(curr_tuple)
            curr_qubits += PS_extra
            curr_tuple = qubit_tuple[:curr_qubits]

            PS_tuple = curr_tuple[old_size:]
            SubR_x = PS_tuple[:max_width]
            SubC_x = PS_tuple[max_width : 2 * max_width]
            PS_ext_row_tuple = PS_tuple[2 * max_width : 2 * max_width + PS_ext_row]
            PS_ext_col_tuple = PS_tuple[
                2 * max_width + PS_ext_row : 2 * max_width + PS_ext_row + PS_ext_col
            ]
            SubR_ancilla = PS_tuple[
                2 * max_width
                + PS_ext_row
                + PS_ext_col : 2 * max_width
                + PS_ext_row
                + PS_ext_col
                + max_width
            ]
            SubC_ancilla = PS_tuple[
                2 * max_width + PS_ext_row + PS_ext_col + max_width :
            ]

            # Set Sub1_x and Sub2_x as 2^1=2, |010>

            Sub_X_Row = 2**e_row
            Sub_X_Col = 2**e_col

            SubC_y = e_dest_index[:e_col] + PS_ext_col_tuple
            SubR_y = e_dest_index[e_col:] + PS_ext_row_tuple
            
            ## Applying PS Gates
            # print('SubR_y')
            # cm.get_local_statevector(qc,SubR_y)
            # print('SubC_y')
            # cm.get_local_statevector(qc,SubC_y)

            if j == 0:
                cm.initialize_value(qc, SubR_x, Sub_X_Row)
                cm.initialize_value(qc, SubC_x, Sub_X_Col)
                # print('SubR_x')
                # cm.get_local_statevector(qc,SubR_x)
                # print('SubC_x')
                # cm.get_local_statevector(qc,SubC_x)
                qc, resSubR = cg.PS(qc, SubR_x, SubR_y, SubR_ancilla)
                qc, resSubC = cg.PS(qc, SubC_x, SubC_y, SubC_ancilla)
            elif j == 1:
                # U1 on Row
                resSubR = SubR_y
                cm.initialize_value(qc, SubC_x, Sub_X_Col)
                # print('SubR_x')
                # cm.get_local_statevector(qc,SubR_x)
                # print('SubC_x')
                # cm.get_local_statevector(qc,SubC_x)
                qc, resSubC = cg.PS(qc, SubC_x, SubC_y, SubC_ancilla)
            elif j == 2:
                # U1 on Column
                resSubC = SubC_y
                cm.initialize_value(qc, SubR_x, Sub_X_Row)
                # print('SubR_x')
                # cm.get_local_statevector(qc,SubR_x)
                # print('SubC_x')
                # cm.get_local_statevector(qc,SubC_x)
                qc, resSubR = cg.PS(qc, SubR_x, SubR_y, SubR_ancilla)
            else:
                resSubR = SubR_y
                resSubC = SubC_y
                # print('SubR_x')
                # cm.get_local_statevector(qc,SubR_x)
                # print('SubC_x')
                # cm.get_local_statevector(qc,SubC_x)
            ## Adding qubits for the parallel multiplier
            
            # print('resSubR')
            # cm.get_local_statevector(qc,resSubR)
            # print('resSubC')
            # cm.get_local_statevector(qc,resSubC)

            Multiplier_Ancilla_value = (((5 * max_width - 3) * max_width) // 2 )+20
            old_size = len(curr_tuple)
            curr_qubits += Multiplier_Ancilla_value
            curr_tuple = qubit_tuple[:curr_qubits]
            Multiplier_ancilla_tuple = curr_tuple[old_size:]

            ## Applying PM Gate
            qc, Multiply_result = cg.PM(qc, resSubR, resSubC, Multiplier_ancilla_tuple)
            
            # print('Multiply_result 1')
            # cm.get_local_statevector(qc,Multiply_result)

            old_size = len(curr_tuple)
            curr_qubits += Multiplier_Ancilla_value
            curr_tuple = qubit_tuple[:curr_qubits]
            Multiplier_ancilla_tuple = curr_tuple[old_size:]
            
            ## Applying PM Gate
            qc, Multiply_result = cg.PM(
                qc, Multiply_result, color_index_tuple, Multiplier_ancilla_tuple
            )

            # print('Multiply_result 2')
            # cm.get_local_statevector(qc,Multiply_result)
            ## Copy the multiply result to the addition ancilla so that data is safe
            cm.multiply_cx(
                qc,
                Multiply_result,
                addition_storage[max_width * j : max_width * (j + 1)],
            )

            work_indices = list(
                range(coord_qubits, coord_qubits + reset_per_calculation)
            )
            qc.reset(work_indices)  ## All 59 qubits reset.

        addition_ancilla = qubit_tuple[
            coord_qubits
            + reset_per_calculation
            + len(addition_storage) : coord_qubits
            + reset_per_calculation
            + len(addition_storage)
            + (3 * max_width)
        ]
        
        # print("Addition Storage:")
        # cm.get_local_statevector(qc,addition_storage[:max_width])
        # cm.get_local_statevector(qc,addition_storage[max_width:2*max_width])
        # cm.get_local_statevector(qc,addition_storage[2*max_width:3*max_width])
        # cm.get_local_statevector(qc,addition_storage[3*max_width:])
        
        division_ancilla = qubit_tuple[
            coord_qubits
            + reset_per_calculation
            + len(addition_storage)
            + (3 * max_width) :
        ]

        ## Add parallel Adder gates
        qc, Addresult1 = cg.PA(
            qc,
            addition_storage[:max_width],
            addition_storage[max_width : 2 * max_width],
            addition_ancilla[:max_width],
        )
        qc, Addresult2 = cg.PA(
            qc,
            Addresult1,
            addition_storage[2 * max_width : 3 * max_width],
            addition_ancilla[max_width : 2 * max_width],
        )
        qc, Addresult = cg.PA(
            qc,
            Addresult2,
            addition_storage[3 * max_width :],
            addition_ancilla[2 * max_width :],
        )

        ## Add normal Divider Gates.AddResult is of max_width wide. For 2 dividions, we need extra 8*max_width ancillae.
        partial_remainder_extra = division_ancilla[:max_width]
        partial_remainder = (
            Addresult + partial_remainder_extra
        )  ##number first, then 0's
        ##SubR_x is the divisor here
        value_init = division_ancilla[max_width : (2 * max_width)]
        cm.initialize_value(qc, value_init, 2 ** (e_row + e_col))
        divisor_extra = division_ancilla[(2 * max_width) : (3 * max_width)]
        divisor = divisor_extra + value_init
        # print("Divisor:")
        # cm.get_local_statevector(qc,value_init)
        quotient = division_ancilla[(3 * max_width) : (4 * max_width)]
        ancilla = division_ancilla[(4 * max_width) : (5 * max_width)]

        qc, quotient, remainder = cg.ND(
            qc, partial_remainder, divisor, quotient, ancilla
        )
        # # Below step is not required when i am deleting the circuit upon every iteration.
        # for index, bit in enumerate(bin_current[::-1]):
        #             if bit == "1":
        #                 qc.x(index)  ## For each 1 in the binary index a NOT gate is applied.

        # Quotient is the final result
        # In bilinear_interpolation_main.py
        result_matrix[i] = cm.get_local_statevector(qc, quotient)
        # cm.save_circuit_snapshot(qc, i) # Uncomment to save the image of the circuit, takes way too long.
        # End of i loop
        qc.data.clear()  # Clear instructions
        del qc  # Delete reference


build_circuit(old_shape, new_shape, gray_value, oracle_gate)

result_2d = result_matrix.reshape(new_shape, order="C")  ## Row major format
print(result_2d)
