import unittest
from service import coordinates


good_hgvs = 'NC_000023.11:g.32389644G>A'
good_hgvs_resp = {
  "alt": "A",
  "assembly": "hg38",
  "chrom": "chrX",
  "hgvs": "NC_000023.11:g.32389644G>A",
  "is_valid": True,
  "original": "NC_000023.11:g.32389644G>A",
  "pos": 32389644,
  "ref": "G"
}

ensembl_hgvs = 'ENST00000380152.8:c.-199A>C'
ensembl_hgvs_resp = {
    'alt': 'C',
    'assembly': 'hg38',
    'chrom': 'chr13',
    'hgvs': 'NC_000013.11:g.32315508A>C',
    'is_valid': True,
    'original': 'ENST00000380152.8:c.-199A>C',
    'pos': 32315508,
    'ref': 'A'
}

intronic_hgvs = 'NM_005101.4(ISG15):c.4-1G>A'
intronic_hgvs_resp = {
    'alt': 'A',
    'assembly': 'hg38',
    'chrom': 'chr1',
    'hgvs': 'NC_000001.11:g.1013983G>A',
    'is_valid': False,
    'original': 'NM_005101.4(ISG15):c.4-1G>A',
    'pos': 1013983,
    'ref': 'G'
}

two_hgvs_request_good = [
    'NM_001002261.3:c.805_809del5',
    'NM_004333.4:c.1799T>A'
]
two_hgvs_request_bad = [
    'NM_001002261.3:c.805_809del5',
    'parse_error_expected'
]

many_hgvs = [
    'NM_000055.4:c.*39G>T',
    'NM_001904.4:c.427_470dup',
    'NM_003907.3:c.636T>A',
    'NM_004366.6:c.2600C>T',
    'NM_178862.3:c.372T>C',
    'NM_000404.4:c.1369C>T',
    'NM_006371.5:c.*2876C>T',
    'NM_001354619.1:c.-593_-592delinsTT'
]

bad_hgvs = 'bad_should_error'
almost_good_hgvs = 'AA_0001234.1:g.12345a>c'

class TestServiceCoordinates(unittest.TestCase):
    def test_format_ref_or_alt(self):
        upper_a = coordinates.format_ref_or_alt('A')
        self.assertEqual('A', upper_a)
        lower_a = coordinates.format_ref_or_alt('a')
        self.assertEqual('A', lower_a)
        empty = coordinates.format_ref_or_alt('')
        self.assertEqual('-', empty)

    def test_coordinates_good_hgvs(self):
        resp = coordinates.get_coordinates(good_hgvs)
        self.assertEqual(good_hgvs_resp, resp)

    def test_coordinates_intronic_hgvs(self):
        resp = coordinates.get_coordinates(intronic_hgvs)
        self.assertEqual(intronic_hgvs_resp, resp)

    def test_coordinates_ensembl_hgvs(self):
        resp = coordinates.get_coordinates(ensembl_hgvs)
        self.assertEqual(ensembl_hgvs_resp, resp)

    def test_all_coordinates_two_strings(self):
        resp = coordinates.get_all_coordinates(two_hgvs_request_good)
        self.assertEqual(2, len(resp['coordinates']))

    def test_all_coordinates_two_strings_with_one_error(self):
        resp = coordinates.get_all_coordinates(two_hgvs_request_bad)
        self.assertEqual(1, len(resp['coordinates']))
        self.assertEqual(1, len(resp['errors']))

    def test_all_coordinates_many_strings(self):
        resp = coordinates.get_all_coordinates(many_hgvs)
        self.assertEqual(8, len(resp['coordinates']))
        has_errors = 'errors' in resp
        self.assertFalse(has_errors)

    def test_coordinates_bad_hgvs(self):
        resp = coordinates.get_coordinates(bad_hgvs)
        self.assertTrue(resp.find('HGVSParseError') >= 0)

    def test_coordinates_almost_good_hgvs(self):
        resp = coordinates.get_coordinates(almost_good_hgvs)
        self.assertTrue(resp.find('HGVSDataNotAvailableError') >= 0)


if __name__ == '__main__':
    unittest.main()
