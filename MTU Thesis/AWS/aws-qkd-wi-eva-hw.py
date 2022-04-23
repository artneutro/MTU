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
# Python script aws-qkd-wi-eva-hw.py 
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

    # Setup eavesdropped protocol
    print('Simulating eavesdropped protocol')
    
    #alice_state = [np.random.randint(0, 2) for _ in range(num_qubits)]
    
    # Get the file header (2 bytes for the experiments) to check with the QKD protocol
    file_name=sys.argv[1]
    file_open=open(file_name,'r')
    first_byte=os.pread(file_open.fileno(), 1, 14)
    second_byte=os.pread(file_open.fileno(), 1, 15)
    alice_key='{0:08b}'.format(ord(first_byte))+'{0:08b}'.format(ord(second_byte))
    alice_state = []
    
    # Only 4 qubits to pair with IBM limitation (AWS HW is limited to 11)
    j = 0
    for i in alice_key:
        if j == 4:
            break;
        alice_state.append(int(i))   
        j += 1
    print("ALICE STATE = ", alice_state)
    
    # 
    np.random.seed(200)  # Seed random generator for consistent results
    
    alice_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    print("ALICE BASIS = ", alice_basis)
    
    bob_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    print("BOB BASIS = ", bob_basis)
    
    eve_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    print("EVE BASIS = ", eve_basis)

    expected_key = bitstring(
        [alice_state[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )

    # Eve intercepts the qubits

    alice_eve_circuit = make_bb84_circ(num_qubits, alice_basis, eve_basis, alice_state)

    # Run simulations.
    repetitions = 1
    #result = cirq.Simulator().run(program=alice_eve_circuit, repetitions=repetitions)
    #eve_state = [int(result.measurements[str(i)]) for i in range(num_qubits)]

    # Set the quantum computer as device
    device = AwsDevice("arn:aws:braket:::device/qpu/ionq/ionQdevice")

    # run circuit
    m_shots = 1
    result = device.run(alice_eve_circuit, shots = m_shots).result()

    # get measurement shots
    counts = result.measurement_counts.keys()

    # print counts
    eve_state = list(counts)[0]    
    print("EVE STATE = ", eve_state)
    
    # Result of the measure is Bob's key candidate
    eve_key = bitstring(
        [eve_state[i] for i in range(num_qubits) if alice_basis[i] == eve_basis[i]]
    )
    print("EVE KEY = ", eve_key)

    eve_bob_circuit = make_bb84_circ(num_qubits, eve_basis, bob_basis, eve_state)

    # Run simulations.
    repetitions = 1
    #result = cirq.Simulator().run(program=eve_bob_circuit, repetitions=repetitions)
    #result_bitstring = bitstring([int(result.measurements[str(i)]) for i in range(num_qubits)])

    # Set the quantum computer as device
    device = AwsDevice("arn:aws:braket:::device/qpu/ionq/ionQdevice")

    # run circuit
    m_shots = 1
    result = device.run(eve_bob_circuit, shots = m_shots).result()

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

    assert expected_key != obtained_key, "Keys shouldn't match"

    circuit = alice_eve_circuit + eve_bob_circuit
    print(circuit)
    print_results(alice_basis, bob_basis, alice_state, expected_key, obtained_key)
    
    # Added for the main program to get results.
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









