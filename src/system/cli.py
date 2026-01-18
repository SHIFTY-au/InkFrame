import argparse

from datetime import timedelta
from config import load_config
from system.scheduler import RefreshScheduler
from main import main

if __name__ == '__main__':
    config = load_config('config/app.yaml')
    scheduler = RefreshScheduler(config)

    parser = argparse.ArgumentParser(description="Weather dashboard application control")
    subparsers = parser.add_subparsers(dest="command")
    refresh_parser = subparsers.add_parser("refresh", help="Refresh the display")
    status_parser = subparsers.add_parser("status", help="Show refresh status")
    args = parser.parse_args()

    if args.command == 'refresh':
        main(force=True)
    if args.command == 'status':
        last_refresh, interval = scheduler.get_last_refresh_info()
        next_refresh = last_refresh + timedelta(hours=interval)
        print(f"Last refresh: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Next refresh: {next_refresh.strftime('%Y-%m-%d %H:%M:%S')}")