# This project is licensed under the MIT License
# See the LICENSE file in the root directory for more information

import subprocess
import sys
import os


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    UNDERLINE = '\033[4m'


# List of available AWS regions
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


def print_available_regions():
    print("Available regions:")
    for region in AVAILABLE_REGIONS:
        print(f" {Colors.GREEN}-{Colors.RESET} {region}")


def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Command failed: {command}")
        # Удаляем вывод ошибки, если это нужно
        sys.exit(1)



def is_file_empty(file_path):
    """Check if a file exists and is empty."""
    return not os.path.exists(file_path) or os.path.getsize(file_path) == 0


def scan_region(region, rate):
    """Perform a scan on the specified AWS region."""
    ip_ranges_command = (
        f"wget -qO- https://ip-ranges.amazonaws.com/ip-ranges.json | "
        f"jq '.prefixes[] | select(.region == \"{region}\") | .ip_prefix' -r | "
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

    if not is_file_empty(f"{region}-range.tlsopen"):
        tls_scan_command = f"cat {region}-range.tlsopen | tls-scan --port=443 -o {region}-range-tlsinfo.json"
        run_command(tls_scan_command)

        convert_to_csv(region)
    else:
        print(f"{Colors.RED}[WARNING]{Colors.RESET} TLS open IPs file is empty, skipping CSV conversion.")


def convert_to_csv(region):
    """Convert TLS info JSON to CSV format for different JSON structures."""
    json_file = f"{region}-range-tlsinfo.json"
    csv_file = f"{region}-range-tlsinfo.csv"

    if is_file_empty(json_file):
        print(f"{Colors.RED}[WARNING]{Colors.RESET} TLS info file {json_file} is empty or missing, skipping CSV conversion.")
        return

    # Attempt to convert JSON to CSV using various jq commands
    csv_commands = [
        f"jq -r '.[] | {{ip, commonName: .cert.subject.commonName}} | [.ip, .commonName] | @csv' {json_file} > {csv_file}",
        f"jq -r '.[] | {{ip, commonName: .cert.subject.commonName}} | [.ip, .commonName] | @csv' {json_file} > {csv_file}",
        f"jq -r '[.ip, .cert.subject.commonName] | @csv' {json_file} > {csv_file}",
        f"jq -r '[.ip, .commonName] | @csv' {json_file} > {csv_file}"
    ]

    for command in csv_commands:
        try:
            run_command(command)
            print(f"{Colors.GREEN}[+]{Colors.RESET} TLS info converted to CSV and saved to {csv_file}")
            return
        except:
            continue  # Try the next command if the current one fails

    print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to convert {json_file} to CSV.")


def main():
    if os.geteuid() != 0:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} You must run this script as the root user.")
        sys.exit(1)

    while True:
        print(f"{Colors.UNDERLINE}awscan{Colors.RESET} > ", end='')
        user_input = input()

        if user_input == "help":
            print_help()
        elif user_input == "list_regions":
            print_available_regions()
        elif user_input.startswith("scan"):
            _, region, rate = user_input.split()
            if region not in AVAILABLE_REGIONS:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} You must specify a correct region.")
                continue
            scan_region(region, int(rate))


def print_help():
    """Display help information for commands."""
    print(f"""Description: AWS IP range scanner with Masscan and TLS analysis made by q1ncite
Core commands
=============

       Command                     Description
    -------------                 -------------
    list_regions                    Show available regions for scanning.
    scan <region> <rate>            Start scan of region (e.g., {Colors.RED}scan eu-central-1 10000{Colors.RESET}).
""")


if __name__ == "__main__":
    main()
