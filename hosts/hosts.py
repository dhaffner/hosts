#!/usr/bin/env python

import os
import os.path
import re

from itertools import ifilterfalse as filterfalse
from operator import methodcaller

import baker

from six.moves import map, filter, zip


def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


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


def _get_slug(text, pattern=_match_slug):
    search = pattern.search(text)
    if search:
        return search.group(1)


def _filter_path(path, slug=re.compile('^\w')):
    if isinstance(path, basestring):
        path = path.split('/')

    return tuple(filter(slug.match, path))


def _read_lines(filename, strip_comments=False):
    with open(filename, 'Ur') as f:
        lines = f.readlines()

    lines = filter(len, map(_strip, lines))

    if strip_comments:
        lines = filterfalse(_iscomment, lines)

    return tuple(lines)


def _read_hosts(filename):
    '''Return all hosts from a given file. All comments and blank lines
    are stripped.
    '''

    with open(filename, 'Ur') as f:
        lines = f.readlines()

    # Strip extraneous whitespace.
    lines = map(_strip, lines)

    # Filter out blanks.
    lines = filter(len, lines)

    # Filter out comments.
    hosts = []

    section_path = []
    section_hosts = []
    for line in lines:
        if not _iscomment(line):
            section_hosts.append(line)
            continue

        match = _match_open.search(line)
        if match is not None:
            section_path.append(match.group(1))
            continue

        match = _match_close.search(line)
        if match is not None:
            if len(section_hosts):
                hosts.append((list(section_path), list(section_hosts)))
                section_hosts = []
            section_path.pop()

    return tuple(hosts)


def _read_structure(infile=None, include_hosts=True):
    '''Determine and return the organizational structure from a given
    host file.
    '''

    path, hosts, structure = [], [], []

    lines = _read_lines(infile)
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
                structure.append((list(path), list(hosts)))
                hosts = []
            else:
                structure.append(list(path))
            path.pop()

    return tuple(structure)


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
                    print _close(s)
        else:
            relative_path = section

        for s in relative_path:
            print _open(s)

        if func(section):
            hosts = map(transform, hosts)

        for h in hosts:
            print h

        print _close(section[-1])
        prev_section = section

    if prev_section:
        for s in reversed(prev_section[1:]):
            print _close(s)


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


def _build_hosts_file(dirname, excludes=None):
    lines = list()
    append, extend = lines.append, lines.extend
    prev, curr = None, None

    for root, dirs, files in os.walk(dirname):

        curr = list(_filter_path(root))[1:]
        if prev and (len(prev) > len(curr) or
                     (len(prev) == len(curr) and prev[-1] != curr[-1])):
            append(_close(prev[-1]))

        if len(curr):
            append(_open(curr[-1]))

        elif files.count('localhost'):
            files.remove('localhost')
            files.insert(0, 'localhost')

        for filename in files:
            hosts = _read_lines(os.path.join(root, filename), strip_comments=True)

            section, _ = os.path.splitext(filename)
            path = curr + [section]
            if _path_in_list(path, excludes):
                hosts = map('#'.__add__, hosts)

            append(_open(section))
            extend(hosts)
            append(_close(section))

        prev = curr

    if prev:
        parents = _filter_path(prev)
        extend(map(_close, reversed(parents)))

    return lines


@baker.command
def generate(dirname, *excludes):

    def scrub(section):
        return section[1:].split('.')

    excludes = map(scrub, filter(methodcaller('startswith', '-'), excludes))

    lines = _build_hosts_file(dirname, excludes=list(excludes))
    for line in lines:
        print line


@baker.command
def paths(infile='/etc/hosts'):
    structure = _read_structure(infile, include_hosts=False)
    for path in map(_join, structure):
        print path


@baker.command
def enable(infile='/etc/hosts', *includes):
    structure = _read_structure(infile, include_hosts=True)
    includes = list(map(_split, includes))
    sift = lambda h: _path_in_list(h, includes)

    _sift_structure(sift, structure, _scrub_comment)


@baker.command
def disable(infile='/etc/hosts', *excludes):
    structure = _read_structure(infile, include_hosts=True)
    excludes = list(map(_split, excludes))
    sift = lambda h: _path_in_list(h, excludes)
    _sift_structure(sift, structure, _add_comment)


def run():
    baker.run()
