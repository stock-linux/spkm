#!/usr/bin/env python

import argparse
import operations

from config import *

parser = argparse.ArgumentParser(
                    prog='spkm',
                    description='Stock PacKage Manager',
                    )

subparsers = parser.add_subparsers(dest='operation')

add_parser = subparsers.add_parser('add', help='Adds some packages to your system.', description='Adds some packages to your system.')
del_parser = subparsers.add_parser('del', help='Deletes some packages from your system.', description='Deletes some packages from your system.')
sync_parser = subparsers.add_parser('sync', help='Sync with remote repos.', description='Sync with remote repos.')
info_parser = subparsers.add_parser('info', help='Displays information about the given package.', description='Displays information about the given package.')
up_parser = subparsers.add_parser('up', help='Upgrades your system.', description='Upgrades your system.')
conf_parser = subparsers.add_parser('conf', help='Displays your SPKM configuration.', description='Displays your SPKM configuration.')

add_parser.add_argument('packages', type=str, nargs='*', help='Packages to add')
del_parser.add_argument('packages', type=str, nargs='*', help='Packages to delete')
info_parser.add_argument('package', type=str, help='Package to display')

args = parser.parse_args()
config = get_config()

if args.operation == 'add':
    operations.add(args.packages)
elif args.operation == 'del':
    operations.delete(args.packages)
elif args.operation == 'sync':
    operations.sync()
elif args.operation == 'info':
    operations.info(config, args.package)
elif args.operation == 'up':
    operations.up()
elif args.operation == 'conf':
    operations.config(config)