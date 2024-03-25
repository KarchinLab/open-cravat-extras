import vcf
from pathlib import Path
import sys
import argparse
import sqlite3
import gzip
import cravat
import traceback
import re
import urllib.request
import os

def ltrim(a, b):
    head = ''
    while (a and b and (a[0] == b[0])):
        head += a[0]
        a = a[1:]
        b = b[1:]
    return head, a, b

parser = argparse.ArgumentParser()
parser.add_argument('input', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()

if args.output.exists():
    args.output.unlink()
db = sqlite3.connect(str(args.output))
c = db.cursor()
c.execute('pragma journal_mode=memory')
c.execute('create table clinvar (alleleid text primary key, clinvar_id text, rev_stat text, sig text, disease_names text, disease_refs text)')
c.execute('create table variant (transcript text, hgvsp text, pos int, ref text, alt text, alleleid text, foreign key(alleleid) references clinvar(alleleid))')

reader = vcf.Reader(args.input.open())

mapper = cravat.get_live_mapper('hg38')

error_variants = open('error_variants.txt','w')
qt_clinvar = 'insert into clinvar (alleleid, clinvar_id, rev_stat, sig, disease_names, disease_refs) values (?, ?, ?, ?, ?, ?)'
qt_variant = 'insert into variant (transcript, hgvsp, pos, ref, alt, alleleid) values (?, ?, ?, ?, ?, ?)'
for n, record in enumerate(reader):
    if not n%10000: print(n, end='\r')
    # if n>50000: break
    clindata = None
    variants = None
    info = record.INFO
    if 'pathogenic' not in [x.lower() for x in info.get('CLNSIG',[])]:
        continue
    crv = {}
    chrom = 'chr'+record.CHROM
    if chrom == 'chrMT':
        chrom = 'chrM'
    crv['chrom'] = chrom
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
    crv['pos'] = pos
    crv['ref_base'] = ref
    crv['alt_base'] = alt
    alleleid = info['ALLELEID']
    clindata = (
        alleleid,
        record.ID,
        ','.join(info['CLNREVSTAT']) if 'CLNREVSTAT' in info else None,
        ','.join(info['CLNSIG']) if 'CLNSIG' in info else None,
        ','.join(map(str,info['CLNDN'])) if 'CLNDN' in info else None,
        ','.join(map(str,info['CLNDISDB'])) if 'CLNDISDB' in info else None,
    )
    c.execute(qt_clinvar, clindata)
    try:
        crx = mapper.map(crv)
    except:
        error_variants.write('\t'.join((crv['chrom'],str(crv['pos']),'+',crv['ref_base'],crv['alt_base'],'errors'))+'\n')
        continue
    mappings = cravat.inout.AllMappingsParser(crx['all_mappings'])
    variants = []
    for hit in mappings.get_all_mappings():
        if not hit.achange:
            continue
        pdot_match = re.match(r'p\.([A-Za-z]{3})(\d+)([A-Za-z]{3})$', hit.achange)
        if pdot_match:
            aref, apos, aalt = pdot_match.groups()
        else:
            aref = apos = aalt = None
        c.execute(qt_variant, (hit.transcript, hit.achange, apos, aref, aalt, alleleid))
print(n)

c.execute('create index ps1_idx on variant (transcript, hgvsp)')
c.execute('create index pm5_idx on variant (transcript, pos, ref, alt)')
db.commit()

url ='https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.md5'
urllib.request.urlretrieve(url, 'clinvar.vcf.gz.md5')
oldfile = 'clinvar.vcf.gz.md5'
newfile = 'oldchecksum.md5'
os.rename(oldfile, newfile)

if os.path.exists('clinvar_acmg.sqlite'):
     os.system('~/miniconda3/bin/python3 tester.py "/local/home/mlarsen/clinvar_acmg" "mlarsen@potomacitgroup.com" "kmoad@potomacitgroup.com" "kanderson@potomacitgroup.com"')
else:
    print('The database was not created')

