def PG_Gate(qc, qubits):
    """
    Peres Gate (PG).
    Inputs: |A, B, C>
    Outputs: |A, A XOR B, A.B XOR C>
    """
    qc.ccx(qubits[0],qubits[1],qubits[2])
    qc.cx(qubits[0],qubits[1])

def TR_Gate(qc, qubits):
    """
    Thapliyal-Ranganathan (TR) Gate.
    Inputs: |A, B, C>
    Outputs: |A, A XOR B, (A . ~B) XOR C> 
    """
    qc.x(qubits[1])
    qc.ccx(qubits[0],qubits[1],qubits[2])
    qc.x(qubits[1])
    qc.cx(qubits[0],qubits[1])

