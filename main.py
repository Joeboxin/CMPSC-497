#This will be used to run CLI commands and open/ send files
import argparse


parser=argparse.ArgumentParser()
parser.add_argument("sub", choices=['Physics', 'Maths', 'Biology'])
args=parser.parse_args()
print ("My subject is ", args.sub)
#Need to implement open server, connecting peer, and sending files commands