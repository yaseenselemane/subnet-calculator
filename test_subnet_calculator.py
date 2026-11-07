"""Run: python -m unittest test_subnet_calculator.py"""
import time
import unittest

from subnet_calculator import calculate_subnet


class SubnetTests(unittest.TestCase):
    def test_slash_26(self):
        r = calculate_subnet('192.168.1.130/26')
        self.assertEqual(r['cidr'], '192.168.1.128/26')
        self.assertEqual((r['first_host'], r['last_host']), ('192.168.1.129', '192.168.1.190'))
        self.assertEqual(r['broadcast'], '192.168.1.191')
        self.assertEqual(r['usable_hosts'], '62')
        self.assertEqual(r['wildcard_mask'], '0.0.0.63')

    def test_dotted_mask_input(self):
        r = calculate_subnet('10.0.0.1 255.255.255.252')
        self.assertEqual((r['cidr'], r['usable_hosts']), ('10.0.0.0/30', '2'))

    def test_point_to_point_31_and_host_32(self):
        r = calculate_subnet('10.1.2.3/31')
        self.assertEqual((r['first_host'], r['last_host'], r['usable_hosts']), ('10.1.2.2', '10.1.2.3', '2'))
        r = calculate_subnet('10.1.2.3/32')
        self.assertEqual((r['first_host'], r['usable_hosts']), ('10.1.2.3', '1'))

    def test_large_network_is_instant(self):
        t = time.time()
        r = calculate_subnet('10.0.0.1/8')
        self.assertLess(time.time() - t, 1)
        self.assertEqual((r['last_host'], r['usable_hosts']), ('10.255.255.254', '16,777,214'))

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            calculate_subnet('bad/99')


if __name__ == '__main__':
    unittest.main()
