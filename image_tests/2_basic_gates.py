from qiskit.circuit.library import UnitaryGate
import numpy as np

def controlled_v(qc,control,target):
    i = 1j
    V_matrix = 0.5 * np.array([[1+i, 1-i], [1-i, 1+i]])

    cv = UnitaryGate(V_matrix).control(1)   # Controlled-V
    
    qc.append(cv, [control, target])
    
    return qc

def controlled_v_plus(qc,control,target):
    i = 1j
    Vdg_matrix = 0.5 * np.array([[1-i, 1+i], [1+i, 1-i]])

    cvdg = UnitaryGate(Vdg_matrix).control(1)  # Controlled-V⁺
    
    qc.append(cvdg, [control, target])
    
    return qc

def PG(qc,qubits):
    '''
    Peres Gate
    qubits: tuple. Should contain indices of 3 qubits on which the PG should be applied.
    '''
    controlled_v(qc,qubits[1],qubits[2])
    controlled_v(qc,qubits[0],qubits[2])
    qc.cx(qubits[0],qubits[1])
    controlled_v_plus(qc,qubits[1],qubits[2])
    
    return qc

def TR(qc,qubits):
    '''
    Thapliyal Ranganathan Gate
    qubits: tuple. Should contain indices of 3 qubits on which the PG should be applied.
    '''
    controlled_v_plus(qc,qubits[1],qubits[2])
    qc.cx(qubits[0],qubits[1])
    controlled_v(qc,qubits[0],qubits[2])
    controlled_v(qc,qubits[1],qubits[2])
    
    return qc


    