import csv

with open('Distance_Matrix.csv', mode='r') as infile:       #Opens the csv file containing the distance matrix
    reader = csv.reader(infile, delimiter=";")
    Distance_Matrix = list(reader)

with open('Duration_Matrix.csv', mode='r') as infile:       #Opens the csv file containing the duartion matrix
    reader = csv.reader(infile, delimiter=";")
    Duration_Matrix = list(reader)

