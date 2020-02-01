import boto3
import psycopg2
import csv
import time
import sys
import os
import datetime
from datetime import date
datetime_object = datetime.datetime.now()
print ("###### Data Pipeline from Redshift ######")
print ("")
print ("Start TimeStamp")
print ("---------------")
print(datetime_object)
print ("")


# Connect to Redshift and Download Table as CSV File

db = psycopg2.connect(dbname='testdb', host='redshift-dc2-test.ctzrqaulg0u6.us-east-1.redshift.amazonaws.com', port='5439', user='awsuser', password='Awsuser1234')
cur = db.cursor()

sql = 'SELECT * from pg_user;'
csv_file_path = '/home/centos/my_csv_file.csv'

try:
    cur.execute(sql)
    rows = cur.fetchall()
finally:
    db.close()

# Continue only if there are rows returned.
if rows:
    # New empty list called 'result'. This will be written to a file.
    result = list()

    # The row name is the first entry for each entity in the description tuple.
    column_names = list()
    for i in cur.description:
        column_names.append(i[0])

    result.append(column_names)
    for row in rows:
        result.append(row)

    # Write result to file.
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            csvwriter.writerow(row)
else:
    sys.exit("No rows found for query: {}".format(sql))

# Upload Generated CSV File to S3 Bucket
s3 = boto3.resource('s3')
bucket = s3.Bucket('redshift-test-shadmha')
s3.Object('redshift-test-shadmha', 'my_csv_file.csv').put(Body=open('/home/centos/my_csv_file.csv', 'rb'))


#Obtaining the connection to RedShift
con=psycopg2.connect(dbname= 'testdb', host='redshift-dc2-test.ctzrqaulg0u6.us-east-1.redshift.amazonaws.com',port= '5439', user= 'awsuser', password= 'Awsuser1234')

#Copy Command as Variable
copy_command="copy pg_user_bkp from 's3://redshift-test-shadmha/my_csv_file.csv' credentials 'aws_iam_role=arn:aws:iam::775867435088:role/SHADMHAREDSHIFT' delimiter '|' region 'ap-southeast-2' ignoreheader 1 removequotes ;"

#Opening a cursor and run copy query
cur = con.cursor()
cur.execute("truncate table pg_user_bkp;")
cur.execute(copy_command)
con.commit()

#Close the cursor and the connection
cur.close()
con.close()

# Remove the S3 bucket file and also the local file
DelLocalFile = 'aws s3 rm s3://redshift-test-shadmha/my_csv_file.csv --quiet'
DelS3File = 'rm /home/centos/my_csv_file.csv'
os.system(DelLocalFile)
os.system(DelS3File)

# Progress Bar Code Ends here

datetime_object_2 = datetime.datetime.now()
print ("End TimeStamp")
print ("-------------")
print (datetime_object_2)
print ("")
