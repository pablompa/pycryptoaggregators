import os
import sys
import time
import multiprocessing

import boto3


with open("aws.txt", 'r') as f:
    for line in f:
        l = line.split("=")
        if len(l) > 1:
            if l[0] == 'id':
                aws_id = l[1].replace("\n", "")
            elif l[0] == 'secret':
                aws_secret = l[1].replace("\n", "")
            elif l[0] == 'bucket':
                aws_bucket = l[1].replace("\n", "")
            elif l[0] == 'path':
                aws_directory = l[1].replace("\n", "")
    

def register_file(filename, period, ref=None):
    if period is None and date is None:
        return
    new_process = multiprocessing.Process(target=_run, args=(filename, period, ref,), daemon=True)
    new_process.start()

    
    
def _run(filename, period, ref):
    print("Creating aws session...")
    sys.stdout.flush()
    aws_session = boto3.session.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
    print("Creating bucket...")
    sys.stdout.flush()
    s3 = aws_session.resource('s3')
    bucket = s3.Bucket(aws_bucket)
    sys.stdout.flush()
    
    while True:
        now = time.time()
        if ref is None:
            ref = now
            
        time.sleep(max(ref - now, 0))
        ref += period
        
        
        print(filename)
        sys.stdout.flush()
#        fstream = open(filename, 'rb')
#        self._bucket.put_object(Key=aws_directory + filename, Body=fstream)
        bucket.upload_file(filename, aws_directory + filename, ExtraArgs={'ACL': 'public-read'})
        print("Filename {} uploaded.".format(filename))
        sys.stdout.flush()
        
        

    
            