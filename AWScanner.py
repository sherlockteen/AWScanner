# This project is licensed under the MIT License
# See the LICENSE file in the root directory for more information

import argparse
import subprocess
import sys


# Определение цветов
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

AVAILABLE_REGIONS = [
    "af-south-1", "ap-east-1", "ap-east-2", "ap-northeast-1", "ap-northeast-2", 
    "ap-northeast-3", "ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", 
    "ap-southeast-3", "ap-southeast-4", "ap-southeast-5", "ap-southeast-6", "ap-southeast-7", 
    "ca-central-1", "ca-west-1", "cn-north-1", "cn-northwest-1", "eu-central-1", 
    "eu-central-2", "eu-north-1", "eusc-de-east-1", "eu-south-1", "eu-south-2", 
    "eu-west-1", "eu-west-2", "eu-west-3", "GLOBAL", "il-central-1", "me-central-1", 
    "me-south-1", "mx-central-1", "sa-east-1", "us-east-1", "us-east-2", "us-gov-east-1", 
    "us-gov-west-1", "us-west-1", "us-west-2"
]

def print_regions():
    print("Available regions:")
    for region in AVAILABLE_REGIONS:
        print(f" {Colors.GREEN}-{Colors.RESET} {region}")

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Command failed: {command}")
        print(e)
        sys.exit(1)

def scan(region, rate):
    ip_ranges_command = (
        f"wget -qO- https://ip-ranges.amazonaws.com/ip-ranges.json | "
        f"jq '.prefixes[] | if .region == \"{region}\" then .ip_prefix else empty end' -r | "
        f"sort -u > {region}-range.txt"
    )
    run_command(ip_ranges_command)
    print(f"{Colors.GREEN}[+]{Colors.RESET} IP ranges for {region} saved to {region}-range.txt")

    masscan_command = f"masscan -iL {region}-range.txt -oL {region}-range.masscan -p 443 --rate {rate}"
    run_command(masscan_command)
    print(f"{Colors.GREEN}[+]{Colors.RESET} Masscan results saved to {region}-range.masscan")

    tls_open_command = f"awk '/open/ {{print $4}}' {region}-range.masscan > {region}-range.tlsopen"
    run_command(tls_open_command)
    print(f"{Colors.GREEN}[+]{Colors.RESET} Open TLS IPs saved to {region}-range.tlsopen")

    tls_scan_command = f"cat {region}-range.tlsopen | tls-scan --port=443 -o {region}-range-tlsinfo.json"
    run_command(tls_scan_command)

    tls_csv_command = (
        f"jq -r '.[] | {{ip, commonName: .cert.subject.commonName}} | [.ip, .commonName] | @csv' {region}-range-tlsinfo.json > {region}-range-tlsinfo.csv"
    )
    
    try:
        run_command(tls_csv_command)
        print(f"{Colors.GREEN}[+]{Colors.RESET} TLS info saved to {region}-range-tlsinfo.csv")
    except:
        alternative_tls_csv_command = (
            f"jq -r ' {{ip, commonName: .cert.subject.commonName}} | [.ip, .commonName] | @csv' {region}-range-tlsinfo.json > {region}-range-tlsinfo.csv"
        )
        run_command(alternative_tls_csv_command)
        print(f"{Colors.GREEN}[+]{Colors.RESET} TLS info saved using alternative command")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS IP range scanner with Masscan and TLS analysis')
    parser.add_argument('--region', type=str, help='AWS region to scan (e.g., eu-central-1)')
    parser.add_argument('--list-regions', action='store_true', help='Show available regions for scanning')
    parser.add_argument('--rate', type=int, default=10000, help='Scan rate for Masscan (default: 10000)')

    args = parser.parse_args()

    if args.list_regions:
        print_regions()
        sys.exit(0)

    if not args.region:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} You must specify a region using --region")
        sys.exit(1)

    scan(args.region, args.rate)
