import unittest

from toolchest.rpm.utils import split_filename, drop_epoch

# Handles DLRN versions
from toolchest.rpm.utils import labelCompare

# Compare vs. baseline
from toolchest.rpm.rpmvercmp import labelCompare as rpmLabelCompare

from toolchest.rpm.utils import cpaas_label_compare


class test_split_filename(unittest.TestCase):

    def test_normal(self):
        assert (split_filename('foo-1.2-1.f23.noarch.rpm') ==
                ('foo', '1.2', '1.f23', '', 'noarch'))
        assert (split_filename('foo-1.2-1.f23.noarch') ==
                ('foo', '1.2', '1.f23', '', 'noarch'))
        assert (split_filename('sos-3.2-36.el7ost.1') ==
                ('sos', '3.2', '36.el7ost.1', '', ''))
        assert (split_filename('sos-3.2-36.el7ost.x86_64') ==
                ('sos', '3.2', '36.el7ost', '', 'x86_64'))
        assert (split_filename('sos-3.2-36.el7ost.1.x86_64') ==
                ('sos', '3.2', '36.el7ost.1', '', 'x86_64'))
        assert (split_filename('sos-3.2-36.el7ost.1.x86_64.rpm') ==
                ('sos', '3.2', '36.el7ost.1', '', 'x86_64'))
        assert (split_filename('sos-3.2-36.el7ost.1.src.rpm') ==
                ('sos', '3.2', '36.el7ost.1', '', ''))
        assert (split_filename('openstack-nova-15.0.1-0.20170222170803.10a32dd.el7ost') ==  # NOQA
                ('openstack-nova', '15.0.1', '0.20170222170803.10a32dd.el7ost', '', ''))   # NOQA
        assert (split_filename('openstack-nova-1:15.0.1-1.el7ost') ==
                ('openstack-nova', '15.0.1', '1.el7ost', '1', ''))

    def test_lead_epoch(self):
        assert (split_filename('2:foo-1.2-1.f23.noarch') ==
                ('foo', '1.2', '1.f23', '2', 'noarch'))
        # error: but, use lead epoch
        assert (split_filename('2:foo-3:1.2-1.f23.noarch') ==
                ('foo', '1.2', '1.f23', '2', 'noarch'))
        assert (split_filename('1:openstack-nova-15.0.1-1.el7ost.noarch') ==
                ('openstack-nova', '15.0.1', '1.el7ost', '1', 'noarch'))
        assert (split_filename('1:openstack-nova-15.0.1-1.el7ost') ==
                ('openstack-nova', '15.0.1', '1.el7ost', '1', ''))

    def test_epoch(self):
        assert (split_filename('foo-3:1.2-1.f23.noarch') ==
                ('foo', '1.2', '1.f23', '3', 'noarch'))

    def test_no_component(self):
        assert (split_filename('1.2-1.f23.noarch') ==
                ('', '1.2', '1.f23', '', 'noarch'))
        assert (split_filename('1.2-1.f23') ==
                ('', '1.2', '1.f23', '', ''))
        assert (split_filename('1.2-1') ==
                ('', '1.2', '1', '', ''))
        assert (split_filename('1.2') ==
                ('', '1.2', '', '', ''))

    def test_absurd(self):
        assert (split_filename('1:aarch64-ppc64le-i686-0.1-1.el7ost.src.rpm') ==
                ('aarch64-ppc64le-i686', '0.1', '1.el7ost', '1', ''))
        assert (split_filename('m-e-g-a-f-o-o-1.0-36.123.1333.elite.omg.long.el7ost.1.noarch.rpm') ==  # NOQA
                ('m-e-g-a-f-o-o', '1.0', '36.123.1333.elite.omg.long.el7ost.1', '', 'noarch'))   # NOQA

    def test_labelCompare(self):

        a = ('0', '6.0.0', '2.el7ost')
        b = ('0', '6.0.1', '0.20170222164853.el7ost')
        c = ('0', '6.0.0', '0.20170217223245.0rc1.el7ost')
        d = ('0', '6.1.10', '0.20170222164853.el7ost')
        e = ('0', '6.1.9', '1.el7ost')
        f = ('0', '6.0.0', '0.2.0rc2.el7ost')
        g = ('0', '6.0.0', '0.3.0rc2.el7ost')
        # new dlrn
        new_dlrn = ('0', '6.1.1', '0.2.20170217063119.ad33b59.el7ost')

        # DLRN build vs not should be different
        self.assertEqual(rpmLabelCompare(a, b), -1)
        self.assertEqual(labelCompare(a, b), 1)
        # Reverse
        self.assertEqual(labelCompare(b, a), -1)

        # Two dlrn builds should be compared the same
        self.assertEqual(rpmLabelCompare(b, c),
                         labelCompare(b, c))

        # One dlrn build and one not with same version
        # should not matter
        self.assertEqual(rpmLabelCompare(a, c),
                         labelCompare(a, c))
        self.assertEqual(rpmLabelCompare(new_dlrn, d),
                         labelCompare(new_dlrn, d))
        self.assertEqual(rpmLabelCompare(new_dlrn, e),
                         labelCompare(new_dlrn, e))
        self.assertEqual(rpmLabelCompare(new_dlrn, b),
                         labelCompare(new_dlrn, b))

        # Micro release difference should work even if it goes from
        # 1-2 digits (or 2-3, etc.)
        self.assertEqual(rpmLabelCompare(d, e), 1)
        self.assertEqual(labelCompare(d, e), -1)
        # Reverse
        self.assertEqual(labelCompare(e, d), 1)

        # Release candidate DLRN builds > dlrn builds
        # e.g. 0.2.0rc1 needs to be > 0.2348349839021890.abc444
        self.assertEqual(rpmLabelCompare(b, f), 1)
        self.assertEqual(rpmLabelCompare(b, g), 1)
        self.assertEqual(labelCompare(b, f), -1)

    def test_cpaas_label_compare(self):

        a = ('0', '6.0.0', '2.el7ost')
        b = ('0', '6.0.0', '3.el7ost')
        c = ('0', '6.0.1', '0.20170.0rc1.el7ost')
        d = ('0', '6.0.1', '1.20170.0rc1.el7ost')
        e = ('0', '6.1.0', '1.20170.0rc1.el7ost')
        f = ('', '6.1.0', '1.20170.0rc1.el7ost')

        self.assertEqual(cpaas_label_compare(a, b), 0)
        self.assertEqual(cpaas_label_compare(b, c), -1)
        self.assertEqual(cpaas_label_compare(c, d), 0)
        self.assertEqual(cpaas_label_compare(d, e), -1)
        self.assertEqual(cpaas_label_compare(e, f), 0)

        # if there's no divider, revert to normal label compare
        a = ('0', '6.0.0', '2')
        b = ('0', '6.0.0', '3')

        self.assertEqual(cpaas_label_compare(a, b), -1)


class test_drop_epoch(unittest.TestCase):

    def test_no_epoch(self):
        assert (drop_epoch('foo-1.2-1.f23.noarch.rpm') ==
                'foo-1.2-1.f23.noarch')
        assert (drop_epoch('foo-1.2-1.f23.noarch') ==
                'foo-1.2-1.f23.noarch')

    def test_epoch(self):
        assert (drop_epoch('foo-0:1.2-1.f23.noarch.rpm') ==
                'foo-1.2-1.f23.noarch')
        assert (drop_epoch('foo-1:1.2-1.f23.noarch') ==
                'foo-1.2-1.f23.noarch')
        assert (drop_epoch('foo-99999:1.2-1.f23.noarch') ==
                'foo-1.2-1.f23.noarch')
        assert (drop_epoch('0:foo-1.2-1.f23.noarch.rpm') ==
                'foo-1.2-1.f23.noarch')
        assert (drop_epoch('99999:foo-1.2-1.f23.noarch') ==
                'foo-1.2-1.f23.noarch')
