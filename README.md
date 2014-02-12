hosts
========

A command line tool for managing [hosts files](http://en.wikipedia.org/wiki/Hosts_file).

The tool relies on the hosts file being formatted a particular way to denote its sections. See [this example](https://github.com/dhaffner/hosts.py/blob/master/example/hosts-1392229946). Sections are indicated via comments like this:

    # <work>
    0.0.0.0 facebook.com
    0.0.0.0 www.facebook.com
    # </work>

Sections may be nested inside other sections.

This formatting was inspired by the organization used in the [hosts files maintained by Dan Pollock](http://someonewhocares.org/hosts/zero/). Hosts files provided on that site should be usable with this script.

## Installation

hosts is installable via pip.

    pip install https://github.com/dhaffner/hosts.git

After that, type `hosts -h` to verify that the install completed successfully.

## Usage

For a full list of options, run:

    hosts -h

#### Specify a hosts file as input and list its sections

    hosts -i /etc/hosts sections

#### Enable a section in a hosts file

    hosts enable work

#### Enable a section in a hosts file that is nested in another section

Use `.` to refer to sections that are nested.

    hosts enable work.distractions

#### Disable a section in a hosts file

    hosts disable spam-sites

#### Print out all hosts in a given section

    hosts show ad-sites

#### Backup a hosts file to a given destination.

    hosts backup ~/.hosts/

#### Install a hosts file.

This command copies a given file to `/etc/hosts`, so it must be run with root priveleges.

    sudo hosts install ~/.hosts/hosts-1392231273

#### Workflow: backup, disable, save, and install

    hosts backup ~/.hosts/
    hosts disable work > ~/.hosts/hosts-work
    sudo hosts install ~/.hosts/hosts-work
