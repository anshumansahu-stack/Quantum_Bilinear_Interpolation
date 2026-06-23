from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFTGate
import numpy as np

def increment_gate(qc, reg):
    """Adds 1 to a quantum register modulo 2^n. reg[0] is LSB."""
    n = len(reg)
    for i in range(n-1, 0, -1):
        controls = reg[0:i]
        if len(controls) == 1:
            qc.cx(controls[0], reg[i])
        else:
            qc.mcx(controls, reg[i])
    qc.x(reg[0])

def U1_Gate(n):
    """
    U1 Gate (+1 adder) as shown in Figure 22.
    """
    reg = QuantumRegister(n, 'q')
    qc = QuantumCircuit(reg, name="U1")
    for i in range(n-1, 0, -1):
        controls = reg[0:i]
        if len(controls) == 1:
            qc.cx(controls[0], reg[i])
        else:
            qc.mcx(controls, reg[i])
    qc.x(reg[0])
    return qc.to_instruction()

def NEQR_Oracle_Gate(n, num_color_qubits, image_matrix=None, gate_name="Oracle"):
    """
    NEQR Oracle Gate.
    """
    if image_matrix is None:
        image_matrix = [[1, 2], [7, 4]]
        
    ny = QuantumRegister(n, 'ny')
    nx = QuantumRegister(n, 'nx')
    c = QuantumRegister(num_color_qubits, 'c')
    qc = QuantumCircuit(ny, nx, c, name=gate_name)
    
    size = 2**n 
        
    for row in range(size):
        for col in range(size):
            val = int(image_matrix[row][col])
            if val == 0:
                continue
                
            row_bin = format(row, f'0{n}b')
            col_bin = format(col, f'0{n}b')
            
            for i, bit in enumerate(reversed(row_bin)):
                if bit == '0': qc.x(ny[i])
            for i, bit in enumerate(reversed(col_bin)):
                if bit == '0': qc.x(nx[i])
                
            val_bin = format(val, f'0{num_color_qubits}b')
            controls = list(ny) + list(nx)
            
            for i, bit in enumerate(reversed(val_bin)):
                if bit == '1':
                    qc.mcx(controls, c[i])
                    
            for i, bit in enumerate(reversed(row_bin)):
                if bit == '0': qc.x(ny[i])
            for i, bit in enumerate(reversed(col_bin)):
                if bit == '0': qc.x(nx[i])
    return qc.to_instruction()

def PS_00_Gate():
    """
    PS Gate for W00 = (2-eY)(2-eX)
    """
    eY = QuantumRegister(1, 'ey')
    eX = QuantumRegister(1, 'ex')
    W00 = QuantumRegister(3, 'w00')
    qc = QuantumCircuit(eY, eX, W00, name="PS")
    
    qc.x(eY)
    qc.x(eX)
    qc.ccx(eY, eX, W00[2])
    qc.x(eY)
    qc.x(eX)
    qc.cx(eY, W00[1])
    qc.cx(eX, W00[1])
    qc.ccx(eY, eX, W00[0])
    
    return qc.to_instruction()

def PS_10_Gate():
    """
    PS Gate for W10 = eY(2-eX)
    """
    eY = QuantumRegister(1, 'ey')
    eX = QuantumRegister(1, 'ex')
    W10 = QuantumRegister(2, 'w10')
    qc = QuantumCircuit(eY, eX, W10, name="PS")
    
    qc.x(eX)
    qc.ccx(eY, eX, W10[1])
    qc.x(eX)
    qc.ccx(eY, eX, W10[0])
    
    return qc.to_instruction()

def PS_01_Gate():
    """
    PS Gate for W01 = (2-eY)eX
    """
    eY = QuantumRegister(1, 'ey')
    eX = QuantumRegister(1, 'ex')
    W01 = QuantumRegister(2, 'w01')
    qc = QuantumCircuit(eY, eX, W01, name="PS")
    
    qc.x(eY)
    qc.ccx(eY, eX, W01[1])
    qc.x(eY)
    qc.ccx(eY, eX, W01[0])
    
    return qc.to_instruction()

def PS_11_Gate():
    """
    PS Gate for W11 = eY * eX
    """
    eY = QuantumRegister(1, 'ey')
    eX = QuantumRegister(1, 'ex')
    W11 = QuantumRegister(1, 'w11')
    qc = QuantumCircuit(eY, eX, W11, name="PS")
    
    qc.ccx(eY, eX, W11[0])
    
    return qc.to_instruction()

def Parallel_Multiplier_Gate(size_a, size_b, size_res):
    """
    Parallel Multiplier (PM) Gate.
    """
    a = QuantumRegister(size_a, 'a')
    b = QuantumRegister(size_b, 'b')
    res = QuantumRegister(size_res, 'res')
    qc = QuantumCircuit(a, b, res, name="PM")
    
    n = size_res
    qc.append(QFTGate(num_qubits=n), res)
    for i in range(size_a):
        for j in range(size_b):
            power = i + j
            for q in range(n):
                phase_pow = power + q - n
                if phase_pow < 0:
                    angle = 2 * np.pi * (2 ** phase_pow)
                    qc.mcp(angle, [a[i], b[j]], res[q])
    qc.append(QFTGate(num_qubits=n).inverse(), res)
    return qc.to_instruction()

def Parallel_Adder_Gate(size_a, size_b, size_res):
    """
    Parallel Adder (PA) Gate.
    """
    a = QuantumRegister(size_a, 'a')
    b = QuantumRegister(size_b, 'b')
    res = QuantumRegister(size_res, 'res')
    qc = QuantumCircuit(a, b, res, name="PA")
    
    n = size_res
    qc.append(QFTGate(num_qubits=n), res)
    for i in range(size_a):
        for q in range(n):
            phase_pow = i + q - n
            if phase_pow < 0:
                angle = 2 * np.pi * (2 ** phase_pow)
                qc.cp(angle, a[i], res[q])
    for i in range(size_b):
        for q in range(n):
            phase_pow = i + q - n
            if phase_pow < 0:
                angle = 2 * np.pi * (2 ** phase_pow)
                qc.cp(angle, b[i], res[q])
    qc.append(QFTGate(num_qubits=n).inverse(), res)
    return qc.to_instruction()

def ND_Gate(size_in, shift_amount):
    """
    Normalization Divider (ND) Gate.
    Performs division by 2^shift_amount by shifting the qubits into a final color register.
    """
    s_in = QuantumRegister(size_in, 's_in')
    c_out = QuantumRegister(size_in - shift_amount, 'c_out')
    qc = QuantumCircuit(s_in, c_out, name="ND")
    
    for i in range(size_in - shift_amount):
        qc.cx(s_in[i + shift_amount], c_out[i])
        
    return qc.to_instruction()
