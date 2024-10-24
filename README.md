![Mine Scan banner image](/images/mine_scan_banner.png)

# Mine Scan - Multi-Threaded Minecraft Server Scanner

A powerful and advanced multi-threaded Python Minecraft Server scanner.
- Retrieves server details such as version, player count, and latency.
- Supports scanning from a file containing *IP* ranges (specified by upper and lower bounds), individual *IP* addresses, or using CIDR notation to define ranges.
- Allows customization of threads, timeout, port, and output file.
- Includes the option to send scan results via Discord webhook, enabling real-time monitoring from anywhere.

## Table of Contents
- [Usage](#usage)
- [How it Works](#how-it-works)
- [Installation](#installation)
- [Using IP Ranges File](#using-ip-ranges-file)
- [To-Do](#to-do)
- [License](#license)
- [Disclaimer](#disclaimer)

# Usage

To run the scan simply execute the script with `python3 minescan.py` and provide the necessary arguments (ensure you have installed the [requirements](#installation)). 

```
usage: tool [-h] [--threads threads] [--timeout seconds] (--filepath filepath | --ip IP) [--port port] [--webhook webhook] [--output output]

options:
  -h, --help                        show this help message and exit
  --threads threads, -th threads    Threads for Pool (default=64)
  --timeout seconds, -ti seconds    Server status timeout (default=2s)
  --filepath filepath, -f filepath  IP ranges file path
  --ip IP, -i IP                    Single IP or CIDR to scan
  --port port, -p port              Minecraft server port (default=25565)
  --webhook webhook, -w webhook     Discord Webhook
  --output output, -o output        Output filepath (default=results.json)

Verify local laws before scanning and ensure you have permission to scan the network. Use at your own risk.
```

The speed of the scan is primarily influenced by threading and timeout settings. Increasing the number of threads enables more simultaneous scans, while reducing the timeout decreases the wait time for responses.

Timeout greatly impacts the speed since each thread must wait for the full timeout duration when there’s no server response before it can move on to the next IP address.

Setting the timeout too low can lead to false timeouts (missing responses from IPs that have servers). Based on testing, a 2-second timeout results in minimal false timeouts.

The scan output is a JSON file containing the successfully scanned servers. This file is updated at the end of each range scan.

A Discord webhook to send the data can be specified but *slightly* increases the time between scans as it has to send the data via requests. 

#### Example

[![asciicast](https://asciinema.org/a/Q1AGTYzjKimuOqJeqDNUy6GGY.svg)](https://asciinema.org/a/Q1AGTYzjKimuOqJeqDNUy6GGY)

After each range scan a summary of the results in the format `HITS|MISSES|TOTAL`.

*Note: Some emojis might not render properly in asciinema depending on your system*

#### Discord Webhook

If a Discord webhook is specified the scan results will be automatically delivered to it. The embedded message looks as follows:

![Discord webhook embed exmaple](/images/embed_example.png)

# How It Works

***Mine Scan*** uses the `mcstatus` Python library to check if a server is running in a specified *IP* and port. If there's a response then certain server data is stored in a JSON file. This data includes:

- Server Version
- Current players and maximum players
- Latency

The program uses `tqdm` to display the progress per-range, `termcolor` to stylize everything and `requests` to send the data to a Discord webhook if provided.

# Installation
To get started download the repository, install the necessary dependencies, and run the script:

1. Clone the repository:

```
git clone https://github.com/Jael-G/Mine-Scan
```

2. Navigate to the project directory:

```
cd Mine-Scan
```

3. Install the required packages:

```
python3 -m pip install -r requirements.txt
```

# Using IP Ranges File

One of the best features of ***Mine Scan*** is its ability to manage large files containing IP addresses. The program supports three different formats for each line:

- IP ranges – specified by lower and upper IP addresses separated with a space.

```
8.8.8.1 8.8.8.254
```

- Specific IPs – a single IP address.

```
192.168.1.1
```

- CIDR ranges – a standard CIDR notation

```
192.168.0.0/24
```

The program generates all possible IP addresses for ranges and CIDR blocks. 

In the [example](#example) the file used was the following:

```
8.8.8.1 8.8.8.254
8.8.4.1 8.8.4.254
192.168.1.1
192.168.0.0/24
```


In testing, a file that contained 478 ranges (around 3.6 million total public IPs) took less than an hour to complete (with an extremely powerful CPU server and thousands of threads).

# To-Do

1. ~~Implement option to allow single IPs and CIDR notation on a file of IP ranges (currently only allows lower and upper range separated by a space).~~ ✅

2. Fix JSON formatting. Currently, it lacks the brackets (`[]`) at the start and end of the file in order to be a properly formatted JSON. 

3. ~~Add Discord webhook implementation to send found servers directly.~~ ✅

# License

```
MIT License

Copyright (c) 2024 Jael Gonzalez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

# Disclaimer

**Usage Responsibility**: This tool is intended for educational and research purposes only. Users are **strongly** advised to verify local laws and obtain permission before scanning any networks or IP addresses. **Unauthorized scanning can violate privacy rights and laws**.

**No Malicious Use**: The creator does not **endorse or take responsibility for any malicious or harmful activities** that may result from the use of this tool. Users must use this software ethically and responsibly, respecting the rights and privacy of others.
