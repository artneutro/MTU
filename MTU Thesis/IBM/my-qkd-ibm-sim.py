#!/usr/bin/python3
# 
# Republic of Ireland
# Munster Technological University
# Department of Computer Science
# COMP9028_27794 - Research Project
# Master Thesis
# Supervisor: Dr. Vincent Emeakaroha
# Student: Jose Lo Huang
#
# Python script my-qkd-ibm-sim.py 
# Based on the script from https://github.com/qiskit-community/qiskit-community-tutorials/blob/master/awards/teach_me_qiskit_2018/cryptography/Cryptography.ipynb
#
# Creation Date: 23/03/2022
# Updates:
# 23/03/2022 - Modify to use the quaternion files as binary input. 
# 
# This code evaluates the quaternion data file header using the QKD protocol.
#

#
# Import the required packages
# 

import sys
import os
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, BasicAer
from qiskit.tools.visualization import plot_histogram

# Creating registers with n qubits
n = 16  # for a local backend n can go as up as 23, after that it raises a Memory Error
qr = QuantumRegister(n, name='qr')
cr = ClassicalRegister(n, name='cr')

# Quantum circuit for alice state
alice = QuantumCircuit(qr, cr, name='Alice')

# Get the file header (2 bytes for the experiments) to check with the QKD protocol
file_name=sys.argv[1]
file_open=open(file_name,'r')
first_byte=os.pread(file_open.fileno(), 1, 14)
second_byte=os.pread(file_open.fileno(), 1, 15)
alice_key='{0:08b}'.format(ord(first_byte))+'{0:08b}'.format(ord(second_byte))

#print("ALICE KEY BINARY = ",alice_key)

# Encode key as alice qubits 
# IBM's qubits are all set to |0> initially
for index, digit in enumerate(alice_key):
    if digit == '1':
        alice.x(qr[index]) # if key has a '1', change state to |1>
        
# Switch randomly about half qubits to diagonal basis
alice_table = []        # Create empty basis table
for index in range(len(qr)):       # BUG: enumerate(q) raises an out of range error
    if 0.5 < np.random.random():   # With 50% chance...
        alice.h(qr[index])         # ...change to diagonal basis
        alice_table.append('X')    # character for diagonal basis
    else:
        alice_table.append('Z')    # character for computational basis

#print("ALICE TABLE = ", alice_table)

# get_qasm method needs the str label
# alternatively we can use circuits[0] but since dicts are not ordered
# it is not a good idea to put them in a func
# circuits = list(qp.get_circuit_names())

def SendState(qc1, qc2, qc1_name):
    ''' This function takes the output of a circuit qc1 (made up only of x and 
        h gates and initializes another circuit qc2 with the same state
    ''' 
    
    # Quantum state is retrieved from qasm code of qc1
    qs = qc1.qasm().split(sep=';')[4:-1]

    # Process the code to get the instructions
    for index, instruction in enumerate(qs):
        qs[index] = instruction.lstrip()

    # Parse the instructions and apply to new circuit
    for instruction in qs:
        if instruction[0] == 'x':
            old_qr = int(instruction[5:-1])
            qc2.x(qr[old_qr])
        elif instruction[0] == 'h':
            old_qr = int(instruction[5:-1])
            qc2.h(qr[old_qr])
        elif instruction[0] == 'm': # exclude measuring:
            pass
        else:
            raise Exception('Unable to parse instruction')

bob = QuantumCircuit(qr, cr, name='Bob')

SendState(alice, bob, 'Alice')    

# Bob doesn't know which basis to use
bob_table = []
for index in range(len(qr)): 
    if 0.5 < np.random.random():  # With 50% chance...
        bob.h(qr[index])        # ...change to diagonal basis
        bob_table.append('X')
    else:
        bob_table.append('Z')

#print("BOB TABLE = ", bob_table)

# Measure all qubits
for index in range(len(qr)): 
    bob.measure(qr[index], cr[index])
    
# Execute the quantum circuit 
backend = BasicAer.get_backend('qasm_simulator')    
result = execute(bob, backend=backend, shots=1).result()
plot_histogram(result.get_counts(bob))

# Result of the measure is Bob's key candidate
bob_key = list(result.get_counts(bob))[0]
bob_key = bob_key[::-1]      # key is reversed so that first qubit is the first element of the list

#print("BOB KEY BINARY = ", bob_key)

keep = []
discard = []
for qubit, basis in enumerate(zip(alice_table, bob_table)):
    if basis[0] == basis[1]:
        #print("Same choice for qubit: {}, basis: {}" .format(qubit, basis[0])) 
        keep.append(qubit)
    else:
        #print("Different choice for qubit: {}, Alice has {}, Bob has {}" .format(qubit, basis[0], basis[1]))
        discard.append(qubit)

acc = 0
for bit in zip(alice_key, bob_key):
    if bit[0] == bit[1]:
        acc += 1

print('Percentage of qubits to be discarded according to table comparison: ', len(keep)/n)
print('Measurement convergence by additional chance: ', acc/n)             

new_alice_key = [alice_key[qubit] for qubit in keep]
new_bob_key = [bob_key[qubit] for qubit in keep]

acc = 0
for bit in zip(new_alice_key, new_bob_key):
    if bit[0] == bit[1]:
        acc += 1        
        
print('Percentage of similarity between the keys: ', acc/len(new_alice_key))              

if (acc//len(new_alice_key) == 1):
    #print("Key exchange has been successfull")
    #print("New Alice's key: ", new_alice_key)
    #print("New Bob's key: ", new_bob_key)
    print("Not Eavesdropped.")
else:
    #print("Key exchange has been tampered! Check for eavesdropper or try again")
    #print("New Alice's key is invalid: ", new_alice_key)
    #print("New Bob's key is invalid: ", new_bob_key)
    print("Eavesdropped.")




