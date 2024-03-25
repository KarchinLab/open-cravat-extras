import urllib.request
import csv
import os
import shutil
import gzip
import hashlib

md5_hash = hashlib.md5()
a_file = open('oldchecksum.md5', "rb")
content = a_file.read()
md5_hash.update(content)
old_check = md5_hash.hexdigest()

url ='https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.md5'
urllib.request.urlretrieve(url, 'clinvar.vcf.gz.md5')
filename = 'clinvar.vcf.gz.md5'
md5_hash = hashlib.md5()
a_file = open(filename, "rb")
content = a_file.read()
md5_hash.update(content)
new_check = md5_hash.hexdigest()

if old_check != new_check:
    os.system('~/miniconda3/bin/python3 clinvar.py')
else:
    print('The checksum is the same')