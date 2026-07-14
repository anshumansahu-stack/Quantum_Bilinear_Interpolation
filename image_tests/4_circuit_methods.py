from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit.circuit import Qubit
import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator
import os
def get_local_statevector(qc, qubit_tuple):
    qc = qc.decompose()
    num_q = qc.num_qubits
    temp_qc = qc.copy()
    temp_qc.measure_all()
    
    sim = AerSimulator(method='matrix_product_state')
    compiled_qc = transpile(temp_qc,
                            basis_gates=['id', 'rz', 'sx', 'x', 'cx'],
                            coupling_map=None,
                            optimization_level=1)
    
    result = sim.run(compiled_qc, shots=1).result()
    full_bitstring = list(result.get_counts().keys())[0].replace(' ', '')
    bits = {i: full_bitstring[num_q - 1 - i] for i in range(num_q)}
    val = sum(int(bits[q]) * (2**i) for i, q in enumerate(qubit_tuple))
    msb_to_lsb_str = "".join(bits[q] for q in reversed(qubit_tuple))
    
    print(f"Indices {qubit_tuple} | Binary(MSB→LSB): {msb_to_lsb_str} | Decimal: {val}")
    return val


# def save_circuit_snapshot(qc, i, folder="circuit_snapshots"):
#     if not os.path.exists(folder):
#         os.makedirs(folder)
#     filename = os.path.join(folder, f"Pixel_{i}.png")
    
#     # No need to slice; the qc is already fresh
#     fig = qc.draw(output='mpl', fold=40, scale=0.6)
#     plt.title(f"Bilinear Interpolation: Pixel {i}")
#     fig.savefig(filename)
#     plt.close(fig) # Critical to prevent memory leaks in Matplotlib
#     print("Circuit saved !")

def save_circuit_snapshot(qc, i, folder="circuit_snapshots"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, f"Pixel_{i}.png")
    
    # idle_wires=False tells Qiskit to hide every qubit that hasn't received a gate yet
    fig = qc.draw(output='mpl', fold=40, scale=0.6, idle_wires=False)
    
    plt.title(f"Bilinear Interpolation: Pixel {i}")
    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig) 
    print(f"Circuit snapshot saved to {filename}!")

def draw_circuit(qc, qubit_tuple=None):
    if qubit_tuple is None:
        print(qc.draw(output='text'))
        return

    from qiskit import QuantumCircuit
    # Filter: Create a mini circuit containing only instructions involving your tuple
    mini_qc = QuantumCircuit(*qc.qregs, *qc.cregs)
    for instruction in qc.data:
        if any(qc.find_bit(q).index in qubit_tuple for q in instruction.qubits):
            mini_qc.append(instruction.operation, instruction.qubits, instruction.clbits)
    
    # idle_wires=False hides the lines for qubits not in your tuple
    print(mini_qc.draw(output='text', idle_wires=False))

def print_state(qc, label, qubit_registers):
    sv = Statevector.from_instruction(qc)
    total = qc.num_qubits

    print(f"\nState at: {label}")
    for idx, amp in enumerate(sv):
        if abs(amp) > 0.01:
            bits = format(idx, f"0{total}b")
            full_display = ""
            for name, qubits in qubit_registers.items():
                # Read from highest index to lowest for standard binary string
                # e.g. P5 P4 P3 P2 P1 P0
                reg_bits = "".join(
                    bits[total - 1 - q] for q in sorted(qubits, reverse=True)
                )
                # Standard decimal conversion (MSB is on the left of reg_bits)
                val = int(reg_bits, 2)
                full_display += f"{name}:{reg_bits}({val}) | "
            print(f"{full_display} Amp: {amp:.3f}")


def initialize_value(qc, qubits, value):
    """
    Initializes a specific integer value into a quantum register using X gates.
    Logic: Little-Endian (index 0 is 2^0).

    Args:
        qc: The QuantumCircuit object.
        qubits: A list or tuple of qubit indices (e.g., (4, 5, 6)).
        value: The integer value to initialize.
    """
    n = len(qubits)
    for i in range(n):
        # Extract the i-th bit of the value using right shift and bitwise AND
        if (value >> i) & 1:
            qc.x(qubits[i])

    return qc


def multiply_cx(qc, control, target):
    """
    Multiply-Controlled Not Operation.
    qc: qubitcircuit.
    control: qubits from which data is to be copied.
    target: qubits to which data is to be copied.
    """
    n = len(control)
    for i in range(n):
        qc.cx(control[i], target[i])

    return qc


def extract_indices(qc):
    circuit_indices = tuple(qc.find_bit(q).index for q in qc.qubits)

    return circuit_indices


def add_qubits(qc, amount):
    new_qubits = [Qubit() for _ in range(amount)]
    qc.add_bits(new_qubits)  # total=11
    return qc

def save_custom_step(qc, step_name, folder="circuit_snapshots"):
    """
    Saves the current state of the circuit to a PNG file.
    Only displays qubits that have gates applied to them.
    """
    # 1. Ensure the directory exists
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # 2. Set the filename based on the provided step_name
    filename = os.path.join(folder, f"{step_name}.png")
    
    # 3. Generate the figure
    # idle_wires=False: removes wires with no gates
    # fold: sets how many gates before wrapping to a new line (adjust as needed)
    # scale: adjusts the size of the gates/text
    try:
        fig = qc.draw(output='mpl', idle_wires=False, fold=50, scale=0.7)
        
        # Optional: Add the step name as a title on the image
        plt.title(f"Circuit Step: {step_name}")
        
        # 4. Save with tight layout to ensure no parts are cut off
        fig.savefig(filename, bbox_inches='tight')
        
        # 5. VERY IMPORTANT: Close the figure to free up memory
        plt.close(fig)
        print(f"Circuit diagram saved: {filename}")
        
    except Exception as e:
        print(f"Error saving {step_name}: {e}")