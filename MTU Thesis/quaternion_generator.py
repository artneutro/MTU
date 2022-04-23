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
# Python Class Generator.py 
# Creation Date: 10/03/2022
# Updates:
# 10/03/2022 - Add functions 
# 
# This code provides the Generator script to create the files with the quaternion data.
#

#
# Import the required packages
# 
import sys
import os
import Quaternion
import Error


def write_quaternion (file_name):
    #
    # This procedure write a quaternion on the file specified.
    # Inputs:
    # - file_name : The name of the file where the new random quaternion will be appended.
    #
    try:
        f = open(file_name, "a")
        quat = Quaternion.Quaternion()
        # Write the quaternion as a string on the file
        f.write(str(quat.print()) + "\n")
        f.close()
    except:
        error = Error.Error()
        error.general_error("writing the quaternion file " + file_name)

def generate_file (n):
    #
    # This procedure creates n files of 1 MB with quaternions (1 per line).
    # Inputs:
    # - n : The number of files to generate.
    # 
    try:
        file_number = 0
        while (file_number < n):
            file_size = 0
            # Files of 1 MB mmax limit
            while (file_size < 1048576):
                write_quaternion("quaternion_data_" + str(file_number) + ".txt")
                file_size = os.path.getsize("quaternion_data_" + str(file_number) + ".txt")
            file_number = file_number + 1
    except:
        error = Error.Error()
        error.general_error("generating the quaternion file " + "quaternion_data_" + str(file_number) + ".txt")


def header():
    #
    # This function shows the header of the program and provide the exit method.
    #
    print("===================================================================")
    print("Quaternion Generator Tool v2.0                                     ")
    print("Powered by Python3, quaternion and NumPy.                          ")
    print("Author: Jose Lo Huang. All rights reserved using the MIT License.  ")
    print("Complete instructions on the README.txt file. Hit Ctrl+C to exit.  ")
    print("===================================================================")


def main():
    header()
    error = Error.Error()
    try:
        n = sys.argv[1]
        if n.isnumeric(): 
            generate_file(int(n))
        else:
            error.not_valid_value(n)
    except:
        error.general_error("main program")


main()


