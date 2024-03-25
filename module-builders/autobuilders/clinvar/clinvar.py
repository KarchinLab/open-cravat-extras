import urllib.request
import gzip
import vcf
import csv
import sqlite3
import os
import shutil
import os.path


def ltrim(a, b):
    head = ''
    while (a and b and (a[0] == b[0])):
        head += a[0]
        a = a[1:]
        b = b[1:]
    return head, a, b


url ='https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz'
urllib.request.urlretrieve(url, 'clinvar.vcf.gz')
with gzip.open('clinvar.vcf.gz', 'r') as f_in, open('clinvar.vcf', 'wb') as f_out:
  shutil.copyfileobj(f_in, f_out)
reader = vcf.Reader(filename='clinvar.vcf')

if os.path.exists('clinvar.sqlite'):
    os.remove("clinvar.sqlite")
db = sqlite3.connect("clinvar.sqlite")
c = db.cursor()
c.execute('pragma journal_mode=memory')
chroms = ['chr'+str(n) for n in range(1,23)]+['chrX','chrY','chrM']
qts = {}
col_order = ['pos','ref','alt','id','disease_refs','disease_names','rev_stat','sig', 'sig_conf']
for chrom in chroms:
    q = f'create table {chrom} (pos int, ref text, alt text, id int, disease_refs text, disease_names text, rev_stat text, sig text, sig_conf text)'
    c.execute(q)
    qts[chrom] = f'insert into {chrom} (pos, ref, alt, id, disease_refs, disease_names, rev_stat, sig, sig_conf) values (?, ?, ?, ?, ?, ?, ?, ?, ?)'
db.commit()
set_chroms = set(chroms)
bad_chroms = open('bad_chroms.txt','w')
for n, record in enumerate(reader):
    if not n%10000: print(n, end='\r')
    drow = []
    try:
        info = record.INFO
        data = {}
        chrom = 'chr'+record.CHROM
        if chrom == 'chrMT':
            chrom = 'chrM'
        if chrom not in set_chroms:
            bad_chroms.write(chrom+'\n')
            continue
        data['chrom'] = chrom
        pos = record.POS
        ref = record.REF
        alt = str(record.ALT[0])
        if alt == 'None': # What are these?
            continue
        head, ref, alt = ltrim(ref, alt)
        pos += len(head)
        if not ref:
            ref = '-'
        if not alt:
            alt = '-'
        data['pos'] = pos
        data['ref'] = ref
        data['alt'] = alt
        data['id'] = int(record.ID)
        data['rev_stat'] = ','.join(info['CLNREVSTAT']) if 'CLNREVSTAT' in info else None
        data['sig'] = ','.join(info['CLNSIG']) if 'CLNSIG' in info else None
        data['sig_conf'] = ','.join(info['CLNSIGCONF']) if 'CLNSIGCONF' in info else None
        refs = info.get('CLNDISDB')
        if refs is None or refs[0] is None:
        	refs = None
        else:
        	refs = ','.join(map(str,refs))
        	refs = refs.replace('_', ' ')
        data['disease_refs'] = refs
        data['disease_names'] = ','.join(filter(None, info['CLNDN'])) if 'CLNDN' in info else None
        if len(record.ALT) > 1:
            print(record)
        if data['rev_stat'] is not None:
        	data['rev_stat'] = str(data['rev_stat']).replace('_', ' ')
        if data['sig'] is not None:
       		data['sig'] = str(data['sig']).replace('_', ' ')
        if data['disease_names'] is not None:
            data['disease_names'] = str(data['disease_names']).replace('_', ' ')          
        if data['sig_conf'] is not None:
            data['sig_conf'] = str(data['sig_conf']).replace('_', ' ')
            
        drow = [data[key] for key in col_order]
        c.execute(qts[chrom], drow)
    except Exception as e:
        print(record)
        print(record.INFO)
        print(drow)
        raise(e)

print(n)

for chrom in chroms:
    print(f'indexing {chrom} ', end='\r')
    q = f'create index {chrom}_index on {chrom} (pos, ref, alt)'
    c.execute(q)
print()
db.commit()

url ='https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.md5'
urllib.request.urlretrieve(url, 'clinvar.vcf.gz.md5')
oldfile = 'clinvar.vcf.gz.md5'
newfile = 'oldchecksum.md5'
os.rename(oldfile, newfile)

if os.path.exists('clinvar.sqlite'):
    os.system('~/miniconda3/bin/python3 tester.py "/local/home/mlarsen/clinvar" "mlarsen@potomacitgroup.com" "kmoad@potomacitgroup.com" "kanderson@potomacitgroup.com"')
else:
    print('The database was not created')
