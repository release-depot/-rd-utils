#!/usr/bin/env python

import re

from toolchest.rpm.rpmvercmp import labelCompare as rpmLabelCompare


def split_filename_fast(nvr):
    info = nvr.rsplit('-', 2)
    return (info[0], info[1], info[2])


# rpmUtils.miscutils and
# dnf.rpm.miscutils are bugged for several types of valid
# rpm names
def splitFilename(nvr):

    #
    # If we have a full rpm name, we'll have an arch
    # or src -
    #   foo-1.2-1.f23.noarch.rpm - 2 dots - arch exists
    #   foo-1.2-1.f23.noarch     - 2 dots - arch exists
    #   foo-1.2-1.noarch.rpm     - 1 dot, arch exists, no disttag
    #   foo-1.2-1.f23            - 1 dot... not 100% deterministic, but
    #                              likely .f23 is a disttag; very rare
    #   1.2-1.f23                - no name, just v, r
    #   1:1.2-1.f23              - no name, just e, v, r
    #   1:foo-1.2-1.f23          - no name, just e, v, r
    #
    # Junk .rpm if it exists
    if nvr[-4:] == '.rpm':
        nvr = nvr[:-4]

    #
    # Any field may be absent
    #
    n = ''
    v = ''
    r = ''
    e = ''
    a = ''

    # Determine arch in a deterministic way
    arches = ['noarch', 'x86_64', 'i386', 'i486', 'i586',
              'i686', 'ppc', 'ppc64', 'ppc64le', 's390',
              's390x', 'aarch64', 'src']
    arch_rx = '\.(' + '|'.join(arches) + ')$'
    if re.search(arch_rx, nvr):
        x = nvr.rfind('.')
        a = nvr[x + 1:]
        if a == 'src':
            # src is not an arch; we just use it for
            # determinism
            a = ''
        nvr = nvr[:x]

    tmp = nvr

    #
    # version & release are after two last dashes, respectively
    # Get 'release' first
    #
    x = tmp.rfind('-')
    if x < 0:
        #
        # maybe someone provided just a version?
        #
        if tmp.rfind('.') >= 0:
            v = tmp
        else:
            n = tmp
        return n, v, r, e, a

    # Release
    r = tmp[x + 1:]
    tmp = tmp[:x]

    x = tmp.rfind('-')
    if x < 0:
        #
        # Someone just provided version-release?
        #
        v = tmp
        return n, v, r, e, a

    #
    # epoch can be in version or in rpm name
    # Check version first
    #
    version = tmp[x + 1:]
    tmp = tmp[:x]

    x = version.rfind(':')
    if x > 0:
        e = version[:x]
        v = version[x + 1:]
    else:
        v = version

    x = tmp.rfind(':')
    if x > 0:
        # We don't want to crash tools if someone
        # somehow got a weird nvr
        # if e != '':
        #    raise ValueError
        e = tmp[:x]
        n = tmp[x + 1:]
    else:
        n = tmp

    return n, v, r, e, a


# Preserve old function name
def split_filename(nvr):
    return splitFilename(nvr)


def dlrn_label_compare(l, r):
    if type(l) is not tuple or type(r) is not tuple:
        raise ValueError('dlrn_label_compare requires two tuples')

    l_is_dlrn = False
    r_is_dlrn = False
    l_is_rc = False
    r_is_rc = False
    l_is_ga = False
    r_is_ga = False

    lx = l[0]
    lv = l[1]
    lr = l[2]

    dlrn_regex = '^0(\.[0-9]{1,2})?\.[0-9]{14}\.'

    if re.match(dlrn_regex, lr):
        l_is_dlrn = True
    elif re.match('^0\.[0-9]{1,2}\.0rc[123](\.|$)', lr):
        l_is_rc = True
    elif re.match('^0\.[0-9]{1,2}(\.|$)', lr):
        l_is_ga = True

    rx = r[0]
    rv = r[1]
    rr = r[2]

    if re.match(dlrn_regex, rr):
        r_is_dlrn = True
    elif re.match('^0\.[0-9]{1,2}\.0rc[123](\.|$)', rr):
        r_is_rc = True
    elif re.match('^0\.[0-9]{1,2}(\.|$)', rr):
        r_is_ga = True

    if r_is_dlrn == l_is_dlrn:
        return (rpmLabelCompare(l, r), False)

    altered = False
    if l_is_dlrn:
        if r_is_rc:
            # print 'fudging DLRN release for right to 1 (RC build)'
            rr = '1'
            altered = True
        if r_is_ga:
            # print 'fudging DLRN release for left to 0 (GA build)'
            lr = '0'
            altered = True
        if rv[:-1] == lv[:-1] and \
           ord(lv[-1:]) - ord(rv[-1:]) == 1:
            # print 'fudging DLRN build version (type 1l)'
            return (rpmLabelCompare((lx, rv, lr), (rx, rv, rr)), True)
        x = lv.rfind('.')
        if lv[:x] == rv:
            # 6.2-2.el6ost > 6.2.1-0.20171313131313
            # print 'fudging DLRN build version (type 2l.b)'
            return (rpmLabelCompare((lx, lv, lr), (rx, lv, rr)), True)
        if lv[:x] == rv[:x]:
            # 6.0.9-1.el7ost > 6.0.10-0.201713131313131
            lm = int(lv[x + 1:])
            rm = int(rv[x + 1:])
            if (lm - rm) == 1:
                # print 'fudging DLRN build version (type 2l)'
                return (rpmLabelCompare((lx, lv, lr), (rx, lv, rr)), True)

    if r_is_dlrn:
        if l_is_rc:
            # print 'fudging DLRN release for left to 1 (RC build)'
            lr = '1'
            altered = True
        if l_is_ga:
            # print 'fudging DLRN release for right to 0 (GA build)'
            rr = '0'
            altered = True
        if rv[:-1] == lv[:-1] and \
           ord(rv[-1:]) - ord(lv[-1:]) == 1:
            # print 'fudging DLRN build version (type 1r)'
            return (rpmLabelCompare((lx, lv, lr), (rx, lv, rr)), True)
        x = rv.rfind('.')
        if rv[:x] == lv:
            # 6.2.1-0.20171313131313 < 6.2-2.el7ost
            # print 'fudging DLRN build version (type 2r.b)'
            return (rpmLabelCompare((lx, lv, lr), (rx, lv, rr)), True)
        if lv[:x] == rv[:x]:
            # 6.0.10-0.201713131313131 < 6.0.9-1.el7ost
            lm = int(lv[x + 1:])
            rm = int(rv[x + 1:])
            if (rm - lm) == 1:
                # print 'fudging DLRN build version (type 2r)'
                return (rpmLabelCompare((lx, lv, lr), (rx, lv, rr)), True)

    # Version are equal, but maybe we altered release
    return (rpmLabelCompare((lx, lv, lr), (rx, rv, rr)), altered)


def label_compare(l, r):
    (ret, is_dlrn) = dlrn_label_compare(l, r)
    return ret


# Preserve old method name
def labelCompare(l, r):
    return label_compare(l, r)


def componentize(builds):
    if builds is None:
        return None
    if type(builds) is str:
        _builds = [builds]
    elif type(builds) is list:
        _builds = builds
    else:
        raise TypeError(
            'Builds is not str or list (' + str(type(builds)) + ')')

    ret = []
    for b in _builds:
        (n, v, r, e, a) = splitFilename(b)
        ret.append(n)

    if type(builds) is str:
        return ret[0]
    return ret
