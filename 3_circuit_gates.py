import importlib
import numpy as np
from qiskit.circuit.library import QFTGate,PhaseGate
bg=importlib.import_module("2_basic_gates")
cm=importlib.import_module("4_circuit_methods")


def U1(qc,qubits):
    '''
    Special Adding one gate
    qc: qubitcircuit.
    qubits: tuple. Should contain indices of n qubits on which the U1 should be applied.
    '''
    n=len(qubits)
    while n>1:
        control=qubits[:n-1] ## first n-1 qubits
        qc.mcx(control,qubits[n-1])
        n-=1
    
    qc.x(qubits[0])
    return qc

## Reversible Half adder is just calling PG once.

def RHA(qc,qubits):
    '''
    Reversible Half adder.
    '''
    
    return bg.PG(qc,qubits)

def RFA(qc,qubits):
    '''
    Reversible Full Adder.
    '''
    firstPGinp=(qubits[0],qubits[1],qubits[3])
    secondPGinp=(qubits[1],qubits[2],qubits[3])
    
    bg.PG(qc,firstPGinp)
    bg.PG(qc,secondPGinp)
    
    return qc

def PA(qc,X,Y,ancilla):
    '''
    Reversible Parallel Adder.
    X: tuple of qubits that represent X.(n bits, 0-->n-1) Output is stored in these n qubits.
    Y: tuple of qubits that represent Y.(n bits, 0-->n-1)
    ancilla: ancillary qubits needed for the parallel addition.(n bits, 0-->n-1)
    
    Return values:
    quantum circuit, and the tuple of qubits in which the addition number is stored.
    '''
    n=len(X)
    RHA(qc,(Y[0],X[0],ancilla[0]))
    for i in range(1,n):
        RFA(qc,(ancilla[i-1],Y[i],X[i],ancilla[i]))

    return qc,X

def RHS(qc,qubits):
    '''
    Reversible Half Subtractor
    qc: qubit circuit
    qubits: tuple of qubits involved in the same.
    '''
    
    bg.TR(qc,qubits)
    qc.cx(qubits[1],qubits[0])
    return qc

def RFS(qc,qubits):
    '''
    Reversible Full Subtractor
    qc: qubit circuit
    qubits: tuple of qubits, size 4, involved in the circuit.
    '''
    RHS(qc,(qubits[0],qubits[2],qubits[3]))
    bg.TR(qc,(qubits[1],qubits[2],qubits[3]))
    return qc

def PS(qc,X,Y,ancilla):
    '''
    Computes Y-X
    Reversible Parallel Subtractor.
    X: tuple of qubits that represent X.(n bits, 0-->n-1) Output is stored in these n qubits.
    Y: tuple of qubits that represent Y.(n bits, 0-->n-1)
    ancilla: ancillary qubits needed for the parallel addition.(n bits, 0-->n-1)
    
    Return values:
    quantum circuit, and the tuple of qubits in which the addition number is stored.
    '''
    n=len(X)
    RHS(qc,(Y[0],X[0],ancilla[0]))
    for i in range(1,n):
        RFS(qc,(ancilla[i-1],Y[i],X[i],ancilla[i]))
    
    return qc,X


def PM(qc,X,Y,ancilla):
    '''
    Reversible Parallel Multiplier.
    X: tuple of qubits that represent X.(n bits, 0-->n-1)
    Y: tuple of qubits that represent Y.(n bits, 0-->n-1)
    ancilla: (5n-3)*n//2 ancilla qubits required for this operation.
    
    total qubits that must be passed in the circuit: ((5n+1)*n//2)
    The measurement method in aersimulator to be used is matrix_product_state.
    '''
    ## Passed state for 4 qubits:|0_0_0_0_y3_y2_y1_y0_x3_x2_x1_x0> Comment all the debug print statements later.
    n=len(X)
    ancillaCounter=0
    for i in range(n):
        for j in range(n):
            qc.ccx(X[i],Y[j],ancilla[ancillaCounter])
            ancillaCounter+=1
        if(i!=n-1):
            ancillaCounter+=i+1 ##This helps keep track of the current qubit.

    ## at the bottom of the circuit, now(n*n-1) qubits shall remain. now, 2*n+ancillaCounter qubits are filled with data.
    
    start,gap=0,1
    addAncilla=(n//2)*((3*n)-1) +20
    qc,finalTuple=PA(qc,ancilla[start:start+n],ancilla[start+n:start+(2*n)],ancilla[addAncilla:addAncilla+n])
    freq=n-2
    start=start+(2*n)+gap
    gap+=1
    addAncilla+=n
    
    while(freq>0):
        qc,finalTuple=PA(qc,finalTuple,ancilla[start:start+n],ancilla[addAncilla:addAncilla+n])
        start=start+gap+n
        gap+=1
        addAncilla+=n
        freq-=1

    # Add all inputs one by one. Apply all parallel adders and add the total result.

    return qc,finalTuple

def LSH(qc,qubits,ancilla):
    '''
    Left Shift Gate (Multiply by 2).
    Logic: Moves bits from lower index to higher index.
    The bit at qubits[n-1] is pushed out into the ancilla.
    '''
    n = len(qubits)
    
    # Step 1: Move the MSB (highest bit) into the ancilla
    qc.swap(qubits[n-1], ancilla)
    
    # Step 2: Cascade swaps downwards to move every bit up by one
    # bit 0 -> bit 1, bit 1 -> bit 2, etc.
    for i in range(n - 1, 0, -1):
        qc.swap(qubits[i], qubits[i-1])
        
    return qc


def Rk(qc,k,control,target,inverse=False,extra_control=None):
    '''
    Conditional k-rotation gate.
    Applies phase rotation e^(2πi/2^k) to |11> state.
    
    Args:
        qc: QuantumCircuit
        k: rotation order (determines angle = 2π/2^k)
        control: control qubit index
        target: target qubit index
        inverse: if False (default), applies positive rotation for addition.
                 if True, applies negative rotation for subtraction.
        extra_control: if provided, adds an additional control qubit
              making this a doubly controlled phase gate.
    
    Ref: Eq.6, Khosropour et al. 2011
    '''
    angle=-2*np.pi/(2**k) if inverse else 2*np.pi/(2**k)
        
    if extra_control is not None:
        qc.append(PhaseGate(angle).control(2), [extra_control, control, target]) ##Applying gate with 2 controls
    else:
        qc.cp(angle, control, target)
    return qc

def draper(qc, b, phi_a, inverse=False, control=None):
    '''
    Quantum carry-save adder/subtractor (Draper method).
    
    Args:
        qc: QuantumCircuit
        b: n qubits in computational basis (number to add/subtract)
        phi_a: n qubits in Fourier basis — QFT of some number a
        inverse: if False (default), computes phi(a+b)
                 if True, computes phi(a-b)
        Just in case the gate is controlled, the control variable is provided.
    
    Output: phi_a is modified in place to encode QFT(a±b).
            Apply QFT⁻¹ after to retrieve result in computational basis.
    
    Ref: Fig.4, Khosropour et al. 2011 / Draper 2000
    '''
    n=len(b)
    for i in range(n):
        curr=i #i=0 apply Rk 1 time
        k=1
        while(curr>=0):
            Rk(qc,k,b[curr],phi_a[n-1-i],inverse=inverse,extra_control=control) #[n-1-i] is to prevent the reversal due to bit-swaps in QFT and iqft
            curr-=1
            k+=1 
    return qc


def ND(qc,partial_remainder,divisor,quotient,ancilla):
    '''
    Parallel Divider Gate.
    
    parameters:
    partial_remainder: 2n qubits, lowest n containing the Numerator and highest n will return the remainder.
    divisor: 2n qubits: highest n containing the divisor and lowest n initialised to 0.
    quotient: separate n qubits that store the quotient.
    ancilla: n ancilla qubits for n left shifts.
    
    total incoming qubits=p=n*6
    '''
    p=len(partial_remainder)
    n=p//2
    remainder=partial_remainder[n:] # Last n bits
    for i in range(n):
        LSH(qc, partial_remainder, ancilla[i])
        qc.append(QFTGate(len(partial_remainder)),partial_remainder)
        draper(qc,divisor,phi_a=partial_remainder,inverse=True)
        qc.append(QFTGate(len(partial_remainder)).inverse(),partial_remainder)
        
        qc.x(partial_remainder[-1])      
        qc.cx(partial_remainder[-1],quotient[-1-i])
        qc.x(partial_remainder[-1])
        
        qc.x(quotient[-1-i])
        qc.append(QFTGate(len(partial_remainder)).control(1), [quotient[-1-i]] + list(partial_remainder))
        draper(qc,divisor,partial_remainder,control=quotient[-1-i])
        qc.append(QFTGate(len(partial_remainder)).inverse().control(1), [quotient[-1-i]] + list(partial_remainder))
        qc.x(quotient[-1-i])
        
        
    return qc,quotient,remainder