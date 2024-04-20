#!/usr/bin/env python

import argparse
import operations

parser = argparse.ArgumentParser(
                    prog='SPKM',
                    description='Stock PacKage Manager',
                    )

subparsers = parser.add_subparsers(help='sub-command help', dest='operation')

add_parser = subparsers.add_parser('add', help='add help')
del_parser = subparsers.add_parser('del', help='del help')
sync_parser = subparsers.add_parser('sync', help='sync help')
info_parser = subparsers.add_parser('info', help='info help')
up_parser = subparsers.add_parser('up', help='up help')

add_parser.add_argument('packages', type=str, nargs='+', help='Packages to add')
del_parser.add_argument('packages', type=str, nargs='+', help='Packages to delete')
info_parser.add_argument('package', type=str, help='Package to display')

args = parser.parse_args()

if args.operation == 'add':
    operations.add(args.packages)
elif args.operation == 'del':
    operations.delete(args.packages)
elif args.operation == 'sync':
    operations.sync()
elif args.operation == 'info':
    operations.info(args.package)
elif args.operation == 'up':
    operations.up()
    
print(args)
