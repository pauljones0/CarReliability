import json
import argparse
import sys
import time
import re
from pathlib import Path
from src.main import ReliabilityAggregator
from src.file_handler import FileHandler

class ReliabilityCLI:
    def __init__(self, data_path='aggregated_reliability.json'):
        self.data_path = data_path
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def run(self, args_list):
        parser = argparse.ArgumentParser(prog='reliability', add_help=False)
        subparsers = parser.add_subparsers(dest='command')

        # reliability ls
        ls_parser = subparsers.add_parser('ls', add_help=False)
        ls_parser.add_argument('make', nargs='?', help='Filter by make')

        # reliability cat
        cat_parser = subparsers.add_parser('cat', add_help=False)
        cat_parser.add_argument('car_key', help='Car key (e.g. Honda_Accord)')

        # reliability grep
        grep_parser = subparsers.add_parser('grep', add_help=False)
        grep_parser.add_argument('pattern', help='Search pattern')

        # reliability fetch (on-demand)
        fetch_parser = subparsers.add_parser('fetch', add_help=False)
        fetch_parser.add_argument('make')
        fetch_parser.add_argument('model')
        fetch_parser.add_argument('--year', type=int)

        # reliability audit
        subparsers.add_parser('audit', add_help=False)

        if not args_list:
            return self.get_usage()

        try:
            args, unknown = parser.parse_known_args(args_list)
        except SystemExit:
            return f"Error: Invalid arguments. Use 'reliability --help' for usage."

        if args.command == 'ls':
            return self.handle_ls(args.make)
        elif args.command == 'cat':
            return self.handle_cat(args.car_key)
        elif args.command == 'grep':
            return self.handle_grep(args.pattern)
        elif args.command == 'fetch':
            return self.handle_fetch(args.make, args.model, args.year)
        elif args.command == 'audit':
            return self.handle_audit()
        else:
            return self.get_usage()

    def get_usage(self):
        return """usage: reliability <command> [args]

Available commands:
  ls [make]          - List available makes or models for a make.
  cat <car_key>      - Show detailed data for a specific car (e.g. Honda_Accord).
  grep <pattern>     - Search for cars or models matching a pattern.
  fetch <make> <mod> - Fetch fresh data for a car (on-demand aggregation).
  audit              - Show current naming audit failures and fill rates.

Use 'reliability <command> --help' for more details.
"""

    def handle_ls(self, make=None):
        if not make:
            makes = sorted(list(set(k.split('_')[0] for k in self.data.keys())))
            return "\n".join(makes)
        
        models = sorted([k.split('_', 1)[1] for k in self.data.keys() if k.lower().startswith(make.lower() + '_')])
        if not models:
            return f"No models found for make: {make}"
        return "\n".join(models)

    def handle_cat(self, car_key):
        # Case insensitive key search
        found_key = next((k for k in self.data.keys() if k.lower() == car_key.lower()), None)
        if not found_key:
            return f"Error: Car '{car_key}' not found. Use 'reliability ls' to see available cars."
        return json.dumps(self.data[found_key], indent=2)

    def handle_grep(self, pattern):
        results = [k for k in self.data.keys() if re.search(pattern, k, re.I)]
        if not results:
            return f"No results found for pattern: {pattern}"
        return "\n".join(results)

    def handle_fetch(self, make, model, year=None):
        print(f"[*] On-demand aggregation for {make} {model}...")
        aggregator = ReliabilityAggregator()
        data = aggregator.aggregate(make, model, year)
        return json.dumps(data, indent=2)

    def handle_audit(self):
        try:
            with open('naming_audit.log', 'r') as f:
                logs = f.readlines()
            return "".join(logs[-20:]) # Last 20 audit entries
        except:
            return "No audit logs found."

if __name__ == "__main__":
    cli = ReliabilityCLI()
    print(cli.run(sys.argv[1:]))
