import logging

from hgvs.easy import *
from hgvs.exceptions import HGVSParseError, HGVSError, HGVSDataNotAvailableError

# hg38 reference dbs and versions per chromosome
hg38_references = {
    'NC_000001.11': 'chr1',
    'NC_000002.12': 'chr2',
    'NC_000003.12': 'chr3',
    'NC_000004.12': 'chr4',
    'NC_000005.10': 'chr5',
    'NC_000006.12': 'chr6',
    'NC_000007.14': 'chr7',
    'NC_000008.11': 'chr8',
    'NC_000009.12': 'chr9',
    'NC_000010.11': 'chr10',
    'NC_000011.10': 'chr11',
    'NC_000012.12': 'chr12',
    'NC_000013.11': 'chr13',
    'NC_000014.9': 'chr14',
    'NC_000015.10': 'chr15',
    'NC_000016.10': 'chr16',
    'NC_000017.11': 'chr17',
    'NC_000018.10': 'chr18',
    'NC_000019.10': 'chr19',
    'NC_000020.11': 'chr20',
    'NC_000021.9': 'chr21',
    'NC_000022.11': 'chr22',
    'NC_000023.11': 'chrX',
    'NC_000024.10': 'chrY',
    'NC_012920.1.1': 'chrM'
}

hg37_references = {
    'NC_000001.10': 'chr1',
    'NC_000002.11': 'chr2',
    'NC_000003.11': 'chr3',
    'NC_000004.11': 'chr4',
    'NC_000005.9': 'chr5',
    'NC_000006.11': 'chr6',
    'NC_000007.13': 'chr7',
    'NC_000008.10': 'chr8',
    'NC_000009.11': 'chr9',
    'NC_000010.10': 'chr10',
    'NC_000011.9': 'chr11',
    'NC_000012.11': 'chr12',
    'NC_000013.10': 'chr13',
    'NC_000014.8': 'chr14',
    'NC_000015.9': 'chr15',
    'NC_000016.9': 'chr16',
    'NC_000017.10': 'chr17',
    'NC_000018.9': 'chr18',
    'NC_000019.9': 'chr19',
    'NC_000020.10': 'chr20',
    'NC_000021.8': 'chr21',
    'NC_000022.10': 'chr22',
    'NC_000023.10': 'chrX',
    'NC_000024.9': 'chrY',
    'NC_012920.1': 'chrM'
}


hg38_prefixes = {
    'chr1': 'NC_000001.11',
    'chr2': 'NC_000002.12',
    'chr3': 'NC_000003.12',
    'chr4': 'NC_000004.12',
    'chr5': 'NC_000005.10',
    'chr6': 'NC_000006.12',
    'chr7': 'NC_000007.14',
    'chr8': 'NC_000008.11',
    'chr9': 'NC_000009.12',
    'chr10': 'NC_000010.11',
    'chr11': 'NC_000011.10',
    'chr12': 'NC_000012.12',
    'chr13': 'NC_000013.11',
    'chr14': 'NC_000014.9',
    'chr15': 'NC_000015.10',
    'chr16': 'NC_000016.10',
    'chr17': 'NC_000017.11',
    'chr18': 'NC_000018.10',
    'chr19': 'NC_000019.10',
    'chr20': 'NC_000020.11',
    'chr21': 'NC_000021.9',
    'chr22': 'NC_000022.11',
    'chrX': 'NC_000023.11',
    'chrY': 'NC_000024.10',
    'chrM': 'NC_012920.1'
}


def format_ref_or_alt(s):
    if s is None or s == '':
        s = '-'
    return s.upper()


def get_coordinates(hgvs):
    # 1. Parse
    try:
        v = parse(hgvs)
    except HGVSParseError as e:
        return repr(e)
    logging.warning(f'v: {str(v)}')

    # 2. Validate
    try:
        valid = validate(v)
    except HGVSError as e:
        return repr(e)
    if not valid:
        return 'Invalid HGVS'

    # 3. Normalize
    try:
        n = normalize(v)
    except HGVSError as e:
        return repr(e)
    logging.warning(f'n: {str(n)}')

    # 4. Map to our transcript versions
    assembly = 'None'
    if n.type == 'c':
        try:
            # try to map to hg38
            g = am38.c_to_g(n)
            assembly = 'hg38'
        except HGVSDataNotAvailableError as e:
            # backup, try to map to hg37
            logging.log(logging.WARNING, repr(e))

        if assembly != 'hg38':
            try:
                g = am37.c_to_g(n)
                assembly = 'hg37'
            except HGVSDataNotAvailableError as e:
                # out of options, can't do it
                return f'HGVS string "{v}" unable to be converted to hg38 or hg37'

    elif n.type == 'g':
        g = n
    else:
        return f'Cannot map HGVS string "{v}" to a g. expression.'
    logging.warning(f'g: {str(g)}, assembly: {assembly}')

    # 5. Check if the g. is in one of our references
    if g.ac in hg38_references.keys():
        chrom = hg38_references[g.ac]
    elif g.ac in hg37_references.keys():
        chrom = hg37_references[g.ac]
    else:
        return f'Reference assembly "{g.ac}" not found in hg38 or hg37'

    return {
        "original": str(hgvs),
        "hgvs": str(g),
        "assembly": assembly,
        "chrom": chrom,
        "pos": g.posedit.pos.start.base,
        "ref": format_ref_or_alt(g.posedit.edit.ref),
        "alt": format_ref_or_alt(g.posedit.edit.alt),
        "is_valid": valid
    }
