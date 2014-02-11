from __future__ import print_function

import os
import os.path
import re
import shutil

from datetime import datetime
from operator import methodcaller

from six.moves import map, filter, zip


#
#   Commands (API)
#


def show(filename, sections=None):
    structure = _read_structure_lazy(filename, include_hosts=True)
    for section, hosts in structure:
        s = _join(section)
        if s not in sections:
            continue
        print(s)
        for host in hosts:
            print(' -', host)


def enable(filename, sections=None):
    '''Enable the given paths in the specified hosts file.'''

    structure = _read_structure_lazy(filename, include_hosts=True)

    sections = list(map(_split, sections))
    sift = lambda h: _path_in_list(h, sections)
    _sift_structure(sift, structure, _scrub_comment)


def disable(filename, sections=None):
    '''Disable the given paths in the specified hosts file.'''

    structure = _read_structure_lazy(filename, include_hosts=True)

    sections = list(map(_split, sections))
    sift = lambda h: _path_in_list(h, sections)
    _sift_structure(sift, structure, _add_comment)


def sections(filename):
    '''Read and print paths from the given hosts file.'''

    structure = _read_structure_lazy(filename, include_hosts=False)
    for path in map(_join, structure):
        print(path)


def install(filename, directory):
    '''Install (copy) a specified hosts file into the given destination.'''

    if directory is None:
        directory = '/etc/'

    shutil.copy(filename, directory)
    print("{} -> {}".format(filename, directory))


def backup(filename, directory=None):
    '''Backup the hosts file to a given directory (default current
    directory).'''

    if directory is None:
        directory = os.getcwd()

    destination = os.path.join(directory,
                               "hosts-{}".format(datetime.now().isoformat()))
    shutil.copy(filename, destination)
    print("{} -> {}".format(filename, destination))


#
#   Helpers
#


_match_close = re.compile('#\s*</([\w\-]+)>')
_match_open = re.compile('#\s*<([\w\-]+)>')
_match_slug = re.compile('#\s*</?([\w\-]+)>')
_match_comment = re.compile('#+(.+)')

_iscomment = methodcaller('startswith', '#')
_open = '# <{}>'.format
_close = '# </{}>'.format
_join = '.'.join
_strip = methodcaller('strip')
_split = methodcaller('split', '.')


def _filter_path(path, slug=re.compile('^\w')):
    if isinstance(path, basestring):
        path = path.split('/')

    return tuple(filter(slug.match, path))


def _read_lines_lazy(filename, strip_comments=False):
    with open(filename, 'Ur') as f:
        if strip_comments:
            for line in f:
                ln = _strip(line)
                if not ln or _iscomment(ln):
                    continue
                yield ln
            return

        for line in f:
            ln = _strip(line)
            if not ln:
                continue
            yield ln
        return


def _read_structure_lazy(infile=None, include_hosts=True):
    '''Determine and return the organizational structure from a given
    host file.
    '''

    path, hosts, structure = [], [], []

    lines = _read_lines_lazy(infile)
    for line in lines:
        if not _iscomment(line):
            if include_hosts:
                hosts.append(line)
            continue

        match = _match_open.search(line)
        if match:
            path.append(match.group(1))
            continue

        match = _match_close.search(line)
        if match:
            if include_hosts:
                yield (list(path), list(hosts))
                hosts = []
            else:
                yield list(path)

            path.pop()
    return


def _sift_structure(func, structure, transform):
    prev_section, relative_path = None, None
    for section, hosts in structure:
        if not (section and hosts):
            continue

        if prev_section:
            common_path = tuple(_common_path(section, prev_section))
            relative_path = section[len(common_path):]
            if len(common_path) == 0:
                for s in prev_section[:-1]:
                    print(_close(s))
        else:
            relative_path = section

        for s in relative_path:
            print(_open(s))

        if func(section):
            hosts = map(transform, hosts)

        for h in hosts:
            print(h)

        print(_close(section[-1]))
        prev_section = section

    if prev_section:
        for s in reversed(prev_section[1:]):
            print(_close(s))


def _common_path(path1, path2):
    for a, b in zip(path1, path2):
        if a == b:
            yield a
        else:
            return


def _path_in_list(path, excludes):
    for exclude in excludes:
        first = exclude[0]
        if first not in path:
            continue
        i = path.index(first)
        subpath = path[i:i + len(exclude)]
        if subpath == exclude:
            return True
    return False


def _scrub_comment(line):
    match = _match_comment.match(line)
    if match:
        return match.group(1)
    return line


def _add_comment(line, format='#'.__add__):
    if _iscomment(line):
        return line
    return format(line)
