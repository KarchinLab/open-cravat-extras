import unittest

from hgvs_api.api.service import coordinates


good_hgvs = 'NC_000023.11:g.32389644G>A'
good_hgvs_resp = {
  "alt": "A",
  "assembly": "None",
  "chrom": "chrX",
  "hgvs": "NC_000023.11:g.32389644G>A",
  "is_valid": True,
  "original": "NC_000023.11:g.32389644G>A",
  "pos": 32389644,
  "ref": "G"
}

ensembl_hgvs = 'ENST00000380152.8:c.-199A>C'


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

    def test_coordinates_ensembl_hgvs(self):
        resp = coordinates.get_coordinates(ensembl_hgvs)
        # TODO see if we can find a way to make ENSEMBL sequences work
        self.assertEqual("HGVSDataNotAvailableError('No transcript definition for (tx_ac=ENST00000380152.8)')", resp)


if __name__ == '__main__':
    unittest.main()
