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
# Python Class Quaternion.py 
# Creation Date: 09/03/2022
# Updates:
# 09/03/2022 - Add functions 
# 
# This code provides the Quaternion class definition.
#

#
# Import the required packages
# 
import numpy as np
import quaternion
import Error

class Quaternion:
    # 
    # The Quaternion class manages the quaternions operations
    #

    def __init__ ( self ):
        #
        # A instantiation of the Quaternion includes an instance of 
        # the Error class and a new quaternion with random values.  
        # 
        self.error = Error.Error()
        self.q = quaternion.as_quat_array(np.random.rand(1,4))

    def print ( self ):
        # 
        # This function prints a quaternion with random values.
        # Inputs:
        # - self : The self instance with the item to print.
        # Outputs:
        # - self.q : The random quaternion item
        #
        try:
            #print(self.q)
            return(self.q)
        except:
            self.error.general_error("printing the quaternion")


