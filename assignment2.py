#!/usr/bin/env python3
import argparse
import os
import sys

"""
                                            --Memory Visualizer--
Student: Kartik
Student ID: k62
Semester: Fall
Academic Honesty Declaration:
The python code in this file is original work written by
Kartik . No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: The following python script visualizes system memory usage and process-specific memory details using bar charts
"""

# Function to turn memory usage percentage into a bar graph
def percent_to_graph(percentage, bar_length=20):
    """
    Converts a percentage into a bar chart using '#' symbols to show usage and
    spaces for the remaining portion.

    Args:
        percentage (float): The memory usage as a fraction between 0 and 1.
        bar_length (int): How long the bar should be (default is 20 characters).

    Returns:
        str: A string that visually represents the memory usage in a bar format.
    """
    filled_length = int(percentage * bar_length)  # Calculate how much of the bar is "filled"
    bar = '#' * filled_length + ' ' * (bar_length - filled_length)  # Fill the rest with spaces
    return bar

# Function to get total system memory
def get_sys_mem():
    """
    Reads the total amount of memory available on the system by checking
    the file /proc/meminfo.

    Returns:
        int: The total system memory in kilobytes (KiB).
    """
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith("MemTotal"):  # Look for the line that specifies total memory
                total_mem = int(line.split()[1])  # Extract the memory value
                return total_mem

# Function to get available system memory
def get_avail_mem():
    """
    Reads how much memory is currently available by checking /proc/meminfo.
    If the 'MemAvailable' field is missing (like in some environments), it
    uses 'MemFree' and 'SwapFree' as a fallback.

    Returns:
        int: The available memory in kilobytes (KiB).
    """
    with open('/proc/meminfo', 'r') as f:
        mem_free = 0
        swap_free = 0
        mem_available = 0
        for line in f:
            if line.startswith("MemFree"):
                mem_free = int(line.split()[1])  # Free memory
            elif line.startswith("SwapFree"):
                swap_free = int(line.split()[1])  # Free swap memory
            elif line.startswith("MemAvailable"):
                mem_available = int(line.split()[1])  # Available memory
       
        # If 'MemAvailable' is missing, calculate it as 'MemFree' + 'SwapFree'
        if mem_available == 0:
            mem_available = mem_free + swap_free
        return mem_available

# Function to convert memory size into a human-readable format
def bytes_to_human_readable(bytes):
    """
    Turns a memory size in bytes into something easier to read (e.g., MiB, GiB).

    Args:
        bytes (int): Memory size in bytes.

    Returns:
        str: The memory size as a string with units like KiB or MiB.
    """
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if bytes < 1024.0:  # If it's small enough for the current unit
            return f"{bytes:.2f} {unit}"  # Format and return
        bytes /= 1024.0  # Otherwise, move to the next unit

# Function to parse user-provided arguments
def parse_command_args():
    """
    Handles command-line arguments using argparse. Users can specify a program
    name, request human-readable memory formats, or change the bar graph length.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Memory Visualizer -- Easily see how memory is being used!")
    parser.add_argument('program', nargs='?', help="The name of a program to check memory usage for. If omitted, shows total memory usage.")
    parser.add_argument('-H', '--human-readable', action='store_true', help="Display memory sizes in a more readable format (e.g., MiB).")
    parser.add_argument('-l', '--length', type=int, default=20, help="Set the length of the bar graph (default: 20).")
    return parser.parse_args()

# Function to find running processes for a program
def pids_of_prog(program):
    """
    Uses the 'pidof' command to get the process IDs (PIDs) of all running
    instances of a program.

    Args:
        program (str): The name of the program to search for.

    Returns:
        list: A list of PIDs associated with the program.
    """
    pids = []
    try:
        pid_list = os.popen(f"pidof {program}").read().strip()
        pids = pid_list.split() if pid_list else []  # Split the PIDs into a list
    except Exception as e:
        print(f"Error finding processes for {program}: {e}")
    return pids

# Function to calculate memory usage of a specific process
def rss_mem_of_pid(pid):
    """
    Checks how much Resident Set Size (RSS) memory a process is using by reading
    its memory map file (/proc/<pid>/smaps).

    Args:
        pid (str): The process ID (PID).

    Returns:
        int: Memory usage in kilobytes (KiB).
    """
    rss_total = 0
    try:
        with open(f"/proc/{pid}/smaps", "r") as f:
            for line in f:
                if line.startswith("Rss"):  # RSS indicates the memory actively used
                    rss_total += int(line.split()[1])  # Add to the total RSS
    except FileNotFoundError:
        print(f"Process {pid} not found.")  # The process might have terminated
    return rss_total

# Following is the main function to tie everything together
def main():
    args = parse_command_args()  # Get user arguments

    # Collect total and available memory stats
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem
    percent_used = used_mem / total_mem

    # Format memory stats as human-readable if requested
    if args.human_readable:
        total_mem_hr = bytes_to_human_readable(total_mem * 1024)
        used_mem_hr = bytes_to_human_readable(used_mem * 1024)
        avail_mem_hr = bytes_to_human_readable(avail_mem * 1024)
    else:
        total_mem_hr = f"{total_mem} KiB"
        used_mem_hr = f"{used_mem} KiB"
        avail_mem_hr = f"{avail_mem} KiB"

    # Print system memory usage as a bar chart
    bar_graph = percent_to_graph(percent_used, args.length)
    print(f"Memory         [{bar_graph} | {percent_used * 100:.0f}%] {used_mem_hr}/{total_mem_hr}")

    # If a program is specified, show its memory usage
    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
            return

        total_prog_rss = sum(rss_mem_of_pid(pid) for pid in pids)

        if args.human_readable:
            total_prog_rss_hr = bytes_to_human_readable(total_prog_rss * 1024)
        else:
            total_prog_rss_hr = f"{total_prog_rss} KiB"

        prog_percent_used = total_prog_rss / total_mem
        print(f"{args.program}        [{percent_to_graph(prog_percent_used, args.length)}] {total_prog_rss_hr}/{total_mem_hr}")

        # Show memory usage for each process individually
        for pid in pids:
            pid_rss = rss_mem_of_pid(pid)
            if args.human_readable:
                pid_rss_hr = bytes_to_human_readable(pid_rss * 1024)
            else:
                pid_rss_hr = f"{pid_rss} KiB"
            pid_percent_used = pid_rss / total_mem
            print(f"{pid}         [{percent_to_graph(pid_percent_used, args.length)}] {pid_rss_hr}/{total_mem_hr}")

if __name__ == "__main__":
    main()
