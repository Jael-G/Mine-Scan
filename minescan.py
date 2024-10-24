from mcstatus import JavaServer, status_response
from multiprocessing.dummy import Pool as ThreadPool
from os import get_terminal_size
from termcolor import colored
from tqdm import tqdm

import argparse
import ipaddress
import json
import time

from webhook import WebhookManager

SEND_TO_WEBHOOK = False


# Prints banner at start
def display_start_banner(args, ranges_amount=1):
    banner_string = """\n███╗   ███╗██╗███╗   ██╗███████╗    ███████╗ ██████╗ █████╗ ███╗   ██╗
████╗ ████║██║████╗  ██║██╔════╝    ██╔════╝██╔════╝██╔══██╗████╗  ██║
██╔████╔██║██║██╔██╗ ██║█████╗      ███████╗██║     ███████║██╔██╗ ██║
██║╚██╔╝██║██║██║╚██╗██║██╔══╝      ╚════██║██║     ██╔══██║██║╚██╗██║
██║ ╚═╝ ██║██║██║ ╚████║███████╗    ███████║╚██████╗██║  ██║██║ ╚████║
╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
                                                                      
         ⛏️  Advanced Minecraft Multi-Threaded Server Scanner
                          
 """

    stats_string = f"📊 Stats:\n"

    if args.ip:
        stats_string += f"\t🎯 Target: {args.ip}\n"
    else:
        stats_string += f"\t🎯 Total Ranges: {ranges_amount}\n"

    stats_string += f"\t🧵 Threads: {thread_num}\n\t⚓ Port: {args.port}\n\t⌛ Timeout: {args.timeout}\n"

    if args.webhook:
        stats_string += f"\t🪝 Webhook: Enabled\n"
    else:
        stats_string += f"\t🪝 Webhook: Disabled\n"

    print(colored(banner_string, "light_red", attrs=["bold"]))
    print(colored(stats_string, "light_yellow"))


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments for the scanner

    Returns:
        argparse.Namespace: Parsed arguments containing threads,
        IP, or filepath.
    """
    arg_parser = argparse.ArgumentParser(
        prog="tool",
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=get_terminal_size().columns
        ),
        description=(
            "Mine Scan - "
            "A powerful advanced multi-threaded Python Minecraft scanner. "
            "Retrieves server details such as version, player count, and latency. "
            "Supports scanning from a file containing IP ranges (specified by upper and lower bounds), "
            "individual IP addresses, or using CIDR notation to define ranges."
        ),
        epilog="Verify local laws before scanning and ensure you have permission to scan the network. Use at your own risk. ",
    )
    arg_parser.add_argument(
        "--threads",
        "-th",
        help="Threads for Pool (default=64)",
        default=64,
        metavar="threads",
    )

    arg_parser.add_argument(
        "--timeout",
        "-ti",
        help="Server status timeout (default=2s)",
        default=2,
        metavar="seconds",
    )

    target_group = arg_parser.add_mutually_exclusive_group(required=True)

    target_group.add_argument(
        "--filepath", "-f", help="IP ranges file path", metavar="filepath"
    )

    target_group.add_argument(
        "--ip", "-i", help="Single IP or CIDR to scan", metavar="IP"
    )

    arg_parser.add_argument(
        "--port",
        "-p",
        help="Minecraft server port (default=25565)",
        default=25565,
        metavar="port",
    )

    arg_parser.add_argument(
        "--webhook",
        "-w",
        help="Discord Webhook",
        default=None,
        metavar="webhook",
    )

    arg_parser.add_argument(
        "--output",
        "-o",
        help="Output filepath (default=results.json)",
        default="results.json",
        metavar="output",
    )

    return arg_parser.parse_args()


def check_server(ip: str, port: int, pbar: tqdm, timeout: float) -> dict:
    """Looks up a server status of a given IP and port

    Args:
        ip (str): Minecraft server ip
        port (int): Defaults to 25565.
        pbar (tqdm): TQDM Bar to update
        timeout (float): Server scan timeout

    Returns:
        dict: Returns dict of server data, empty if no server found
    """

    server_data = {}
    try:
        server = JavaServer.lookup(f"{ip}:{port}", timeout)
        status: status_response.JavaStatusResponse = server.status()

        server_data[ip] = {}
        server_data[ip]["version"] = status.version.name
        server_data[ip]["latency"] = f"{status.latency:.2f}"
        server_data[ip]["players"] = f"{status.players.online}/{status.players.max}"

    except:
        pass

    pbar.update(1)
    return server_data


def generate_target_ips(ip_lower: str, ip_upper: str = None) -> list[str]:
    """Generates all possible IPs

    Args:
        ip_lower (str): The starting IP address or CIDR block.
        ip_upper (str, optional): The ending IP address (for range-based generation).

    Returns:
        list[str]: List target IPs
    """

    if ip_upper:  # Generate using range
        lower = int(ipaddress.ip_address(ip_lower))
        upper = int(ipaddress.ip_address(ip_upper))
        ips = []

        for i in range(lower, upper + 1):
            ips.append(str(ipaddress.ip_address(i)))
        return ips

    if "/" in ip_lower:  # Generate using CIDR
        network = ipaddress.ip_network(ip_lower, strict=False)
        ips = [str(ip) for ip in network.hosts()]
        return ips

    return [ip_lower]  # Return single IP


def parse_results(
    ip_range: str | tuple[str, str], results: list[dict], run_time: float
) -> None:
    """Parses and demonstrates the scan results

    Args:
        ip_range (str | tuple[str, str]): Single IP, CIDR or lower and upper range
        results (list[dict]): List of all server data dicts
        run_time (float): Time to complete scan
    """

    hits_list: list[dict] = [
        server_data for server_data in results if server_data != {}
    ]
    misses = len(results) - len(hits_list)
    total = len(results)

    print(
        colored(
            f"✅ Done → {len(hits_list)}|{misses}|{total} [{run_time:.2f}s]",
            "light_green",
        )
    )

    if SEND_TO_WEBHOOK:
        response = webhook_manager.send_results(
            ip_range, total, len(hits_list), misses, hits_list
        )

        if response == 204:
            print(colored("📩 Sent to webhook", "light_cyan"))
        else:
            print(colored("❌ Request to webhook failed", "light_red"))

    print()

    with open(output_filepath, "a") as json_file:
        for server_data in hits_list:
            json_file.write(f"{json.dumps(server_data)}\n")


def count_lines(filepath: str) -> int:
    """Count the lines in a filepath

    Args:
        filepath (str): IP ranges file

    Returns:
        int: Amount of lines in the file
    """
    with open(filepath, "r") as ranges_file:
        return sum(1 for line in ranges_file)


def execute_thread_pool(
    ip_range: str | tuple[str, str], port: int, thread_num: int, timeout: float
) -> None:
    """Executes thread pool to scan a given IP range

    Args:
        ip_range (str | tuple[str, str]): Single IP, CIDR or lower and upper range
        port (int): Minecraft server port
        thread_num (int): Amount of threads for Pool
        timeout (float): Server scan timeout
    """

    if type(ip_range) == str:
        target_ips = generate_target_ips(ip_range)
    else:
        target_ips = generate_target_ips(ip_range[0], ip_range[1])

    pool = ThreadPool(thread_num)

    start_time = time.time()

    print(colored(f"⚙️  Selected {len(target_ips)} IPs", "light_yellow"))

    with tqdm(
        total=len(target_ips),
        bar_format=colored("{l_bar}{bar}| {n_fmt}/{total_fmt}  ", "light_yellow"),
        unit="IP",
        unit_scale=True,
    ) as pbar:

        try:
            results: list[dict] = pool.map(
                lambda ip: check_server(ip, port, pbar, timeout), target_ips
            )
        except Exception as e:
            print(colored(f"Error occurred: {e}", "red"))
        finally:
            run_time = time.time() - start_time
            pool.close()
            pool.join()

    parse_results(ip_range, results, run_time)


if __name__ == "__main__":
    args: argparse.Namespace = parse_arguments()
    thread_num = int(args.threads)
    timeout = float(args.timeout)
    port = int(args.port)
    output_filepath = args.output

    if args.webhook:
        webhook_manager = WebhookManager(args.webhook)
        SEND_TO_WEBHOOK = True

    if args.ip:  # IP or CIDR
        display_start_banner(args)
        print(colored(f"🔍 Scanning: {args.ip}", "light_cyan"))

        ip_range = args.ip
        execute_thread_pool(ip_range, port, thread_num, timeout)

    else:  # IP range File
        ranges_amout = count_lines(args.filepath)
        display_start_banner(args, ranges_amout)

        with open(args.filepath, "r") as ranges_file:
            for line in ranges_file:
                ip_line = tuple(line.split()[0:2])

                if len(ip_line) == 2:  # Lower and upper range
                    ip_range = tuple(ip_line)
                    print(
                        colored(
                            f"🔍 Scanning: {ip_range[0]} - {ip_range[1]}", "light_cyan"
                        )
                    )

                elif len(ip_line) == 1: # IP or CIDR
                    ip_range = ip_line[0]
                    print(colored(f"🔍 Scanning: {ip_range}", "light_cyan"))

                try:
                    execute_thread_pool(ip_range, port, thread_num, timeout)
                except Exception as e:
                    print(colored(f"Error scanning range: {e}\n", "light_red"))
