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
# Python script aws-qkd-wo-eva-hw.py 
# Based on the script from https://github.com/quantumlib/Cirq/blob/master/examples/bb84.py
#
# Creation Date: 25/03/2022
# Updates:
# 22/04/2022 - Add comments and bug fixes. 
# 
# This code evaluates the quaternion data file header using the QKD protocol.
#

import sys
import os
import numpy as np
import boto3
from braket.aws import AwsDevice
from braket.devices import LocalSimulator
from braket.circuits import Circuit

# get the account ID
aws_account_id = boto3.client("sts").get_caller_identity()["Account"]
# the name of the bucket
my_bucket = "amazon-braket-afbfc6532108"
# the name of the folder in the bucket
my_prefix = "simulation-output"
s3_folder = (my_bucket, my_prefix)

def main(num_qubits=4):
    # Setup non-eavesdropped protocol
    
    print('Simulating non-eavesdropped protocol')
    
    # Commented from the original code
    #alice_state = [np.random.randint(0, 2) for _ in range(num_qubits)]
    
    # Get the file header (2 bytes for the experiments) to check with the QKD protocol
    file_name=sys.argv[1]
    file_open=open(file_name,'r')
    first_byte=os.pread(file_open.fileno(), 1, 14)
    second_byte=os.pread(file_open.fileno(), 1, 15)
    alice_key='{0:08b}'.format(ord(first_byte))+'{0:08b}'.format(ord(second_byte))
    alice_state = []
    
    j = 0
    for i in alice_key:
        if j == 4:
            break;
        alice_state.append(int(i))   
        j += 1
    print("ALICE STATE = ", alice_state)
    
    alice_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    print("ALICE BASIS = ", alice_basis)
    
    bob_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    print("BOB BASIS = ", bob_basis)

    expected_key = bitstring(
        [alice_state[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )
    print("EXPECTED KEY = ", expected_key)

    circuit = make_bb84_circ(num_qubits, alice_basis, bob_basis, alice_state)

    # Run simulations.
    repetitions = 1

    # Set the quantum computer as device
    device = AwsDevice("arn:aws:braket:::device/qpu/ionq/ionQdevice")

    # execute the circuit
    task = device.run(circuit, s3_folder, shots=1)
    
    # display the results
    result = task.result()
    print(task.result().measurement_counts)

    # get measurement shots
    counts = result.measurement_counts.keys()

    # print counts
    list_one = list(counts)[0]    
    print(list_one)
    
    # Result of the measure is Bob's key candidate
    bob_key = bitstring(
        [list_one[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )
    print("BOB KEY BINARY = ", bob_key)

    # This is for compatibility with original code
    obtained_key = bob_key

    assert expected_key == obtained_key, "Keys don't match"
    print(circuit)
    print_results(alice_basis, bob_basis, alice_state, expected_key, obtained_key)
    
    if (expected_key == obtained_key):
        print("Not Eavesdropped.")
    else:
        print("Eavesdropped.")
        

def make_bb84_circ(num_qubits, alice_basis, bob_basis, alice_state):

    qubits = Circuit().i(range(num_qubits))
    circuit = Circuit()

    # Alice prepares her qubits
    alice_enc = []
    for index, _ in enumerate(alice_basis):
        if alice_state[index] == 1:
            alice_enc.append(qubits.x([index]))
        if alice_basis[index] == 1:
            alice_enc.append(qubits.h([index]))
    
    circuit.add(alice_enc)

    # Bob measures the received qubits
    bob_basis_choice = []
    for index, _ in enumerate(bob_basis):
        if bob_basis[index] == 1:
            bob_basis_choice.append(qubits.h([index]))
        
    circuit.add(bob_basis_choice)
    #circuit.add(cirq.measure_each(*qubits))

    return circuit


def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)


def print_results(alice_basis, bob_basis, alice_state, expected_key, obtained_key):
    num_qubits = len(alice_basis)
    basis_match = ''.join(
        ['X' if alice_basis[i] == bob_basis[i] else '_' for i in range(num_qubits)]
    )
    alice_basis_str = "".join(['C' if alice_basis[i] == 0 else "H" for i in range(num_qubits)])
    bob_basis_str = "".join(['C' if bob_basis[i] == 0 else "H" for i in range(num_qubits)])

    print(f'Alice\'s basis:\t{alice_basis_str}')
    print(f'Bob\'s basis:\t{bob_basis_str}')
    print(f'Alice\'s bits:\t{bitstring(alice_state)}')
    print(f'Bases match::\t{basis_match}')
    print(f'Expected key:\t{expected_key}')
    print(f'Actual key:\t{obtained_key}')


if __name__ == "__main__":
    main()





