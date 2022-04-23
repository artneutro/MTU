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
# Python Class Error.py 
# Creation Date: 10/03/2022
# Updates:
# 10/03/2022 - Add functions 
# 
# This code provides the Error class definition.
#

class Error:
    # 
    # The Error class will manage the main and repetitive error messages
    # 

    def __init__ ( self ):
        #
        # The only variable is a dummy text for future purposes
        # 
        self.text = None


    def general_error ( self , msg ):
        #
        # This function is to print a general error message if there is an unexpected error
        # 
        print()
        print("******************************************************************")
        print("There was a problem "+ str(msg) +". Check the following: ")
        print("1. Your internet connection ")
        print("2. Your Python version is 3.8+ ")
        print("3. You have the correct permissions ")
        print("******************************************************************")
        print()


    def not_valid_value ( self , value ):
        #
        # This function will indicate that a value is not valid
        # 
        print("======> " + str(value) + " is not a valid value.")
        print("Please choose a valid value.")
        

