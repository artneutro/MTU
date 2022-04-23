#!/bin/bash
# 
# Republic of Ireland
# Munster Technological University
# Department of Computer Science
# COMP9028_27794 - Research Project
# Master Thesis
# Supervisor: Dr. Vincent Emeakaroha
# Student: Jose Lo Huang
#
# Bash Script data_distributor.sh 
# Creation Date: 21/03/2022
# Updates:
# 22/03/2022 - Bug fixes and improvements
# 
# This code executes the data distribution between the different CSP servers.
# 
# Inputs:
# server_list.txt       - A file containing the IP list of the servers located on the different CSP.
# quaternion_data_*.txt - A set of files with the quaternion data to distribute.
# 

# Check the number of lines in the server_list.txt file.
n=$(wc -l server_list.txt | awk '{print $1}')

echo "There are $n servers."
echo

# Check the number of quaternion files
m=$(ls quaternion_data_*.txt | wc -l)

echo "There are $m quaternion files."
echo

# Get the minimum per server
minim=$((m/n))
echo "The minimum number of files per server is $((m/n))"
echo

# Write the data files on a new file data_list.txt
ls quaternion_data_*.txt > data_list.txt

echo "The data files to send are:"
while read p; do
	echo "$p"  
done < data_list.txt
echo

# Divide the list of m quaternion files between the n server names
cur_server=1
cur_line=1
while read p; do
	count=0
	if [ $cur_server -eq $((n)) ]; then
		echo "Server = $p"
		while [ $cur_line -lt $((m+1)) ]; do
			file_name=$(sed -n "$((cur_line))p" data_list.txt)
			echo "Sending $file_name to $p"
			scp -i pass.pem $file_name ubuntu@$p:~/
			cur_line=$((cur_line+1))
		done
	else
		echo "Server = $p"
		while [ $count -lt $minim ]; do
			file_name=$(sed -n "$((cur_line))p" data_list.txt)
                        echo "Sending $file_name to $p"
			scp -i pass.pem $file_name ubuntu@$p:~/
                        cur_line=$((cur_line+1))
			count=$((count+1))
		done
	fi
	cur_server=$((cur_server+1))
	echo
done < server_list.txt

# Rotate the server list
tac server_list.txt | awk 'NR==1 {line =$0; next} 1; END{print line}' | tac > server_list.txt.tmp 
mv server_list.txt.tmp server_list.txt


