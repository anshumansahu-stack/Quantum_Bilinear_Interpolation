from qiskit import QuantumCircuit,ClassicalRegister,transpile
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Statevector
import numpy as np
import basic_gates as bg
import circuit_gates as cg

# Create a Left Shift circuit for n=15
n=18
qc = QuantumCircuit(n)

# Initialize to |000000010000000111> to test edge case

qc.x(0)
qc.x(1)
qc.x(2)
qc.x(10)

partial_remainder=tuple(range(0,6))
divisor=tuple(range(6,12))
quotient=tuple(range(12,15))
ancilla=tuple(range(15,18))

registers = {
    'anc': [17, 16, 15],
    'Q':   [14, 13, 12],
    'D':   [11, 10, 9, 8, 7, 6],
    'P':   [5, 4, 3, 2, 1, 0]
}

cg.print_state(qc, "After initialization, Begin 1st Iteration", registers)

cg.LSH(qc, partial_remainder, ancilla[0])
cg.print_state(qc, "After LSH", registers)

qc.append(QFTGate(len(partial_remainder)),partial_remainder)
cg.draper(qc,divisor,phi_a=partial_remainder,inverse=True)
qc.append(QFTGate(len(partial_remainder)).inverse(),partial_remainder)
cg.print_state(qc, "After IQFT", registers)

qc.x(partial_remainder[-1])      
qc.cx(partial_remainder[-1],quotient[-1])
qc.x(partial_remainder[-1])      
cg.print_state(qc, "After CNOT", registers)

qc.x(quotient[-1])
qc.append(QFTGate(len(partial_remainder)).control(1), [quotient[-1]] + list(partial_remainder))
cg.draper(qc,divisor,partial_remainder,control=quotient[-1])
qc.append(QFTGate(len(partial_remainder)).inverse().control(1), [quotient[-1]] + list(partial_remainder))
qc.x(quotient[-1])
cg.print_state(qc, "After IQFT draper addition", registers)


cg.print_state(qc, "After initialization, Begin 2nd Iteration", registers)

cg.LSH(qc, partial_remainder, ancilla[1])
cg.print_state(qc, "After LSH", registers)

qc.append(QFTGate(len(partial_remainder)),partial_remainder)
cg.draper(qc,divisor,phi_a=partial_remainder,inverse=True)
qc.append(QFTGate(len(partial_remainder)).inverse(),partial_remainder)
cg.print_state(qc, "After IQFT", registers)

qc.x(partial_remainder[-1])      
qc.cx(partial_remainder[-1],quotient[-2])
qc.x(partial_remainder[-1])      
cg.print_state(qc, "After CNOT", registers)

qc.x(quotient[-2])
qc.append(QFTGate(len(partial_remainder)).control(1), [quotient[-2]] + list(partial_remainder))
cg.draper(qc,divisor,partial_remainder,control=quotient[-2])
qc.append(QFTGate(len(partial_remainder)).inverse().control(1), [quotient[-2]] + list(partial_remainder))
qc.x(quotient[-2])
cg.print_state(qc, "After IQFT draper addition", registers)


cg.print_state(qc, "After initialization, Begin 3rd Iteration", registers)

cg.LSH(qc, partial_remainder, ancilla[2])
cg.print_state(qc, "After LSH", registers)

qc.append(QFTGate(len(partial_remainder)),partial_remainder)
cg.draper(qc,divisor,phi_a=partial_remainder,inverse=True)
qc.append(QFTGate(len(partial_remainder)).inverse(),partial_remainder)
cg.print_state(qc, "After IQFT", registers)

qc.x(partial_remainder[-1])      
qc.cx(partial_remainder[-1],quotient[-3])
qc.x(partial_remainder[-1])      
cg.print_state(qc, "After CNOT", registers)

qc.x(quotient[-3])
qc.append(QFTGate(len(partial_remainder)).control(1), [quotient[-3]] + list(partial_remainder))
cg.draper(qc,divisor,partial_remainder,control=quotient[-3])
qc.append(QFTGate(len(partial_remainder)).inverse().control(1), [quotient[-3]] + list(partial_remainder))
qc.x(quotient[-3])
cg.print_state(qc, "After IQFT draper addition", registers)


