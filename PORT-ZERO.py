#!/usr/bin/env python3

import socket
import threading
import argparse
import sys
from datetime import datetime
import pyfiglet
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
import time

class PortScanner:
    def __init__(self, target, threads=100):
        self.target = target
        self.threads = threads
        self.open_ports = []
        self.lock = threading.Lock()
        
    def resolve_target(self):
        """Resolve hostname to IP address"""
        try:
            self.ip = socket.gethostbyname(self.target)
            return True
        except socket.gaierror:
            print(f"Error: Could not resolve hostname '{self.target}'")
            return False
    
    def ping_host(self):
        """Ping host to check if it's alive (-sn flag)"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.ip]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def scan_port_tcp(self, port):
        """TCP Connect scan (-sS flag simulation)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.ip, port))
            sock.close()
            
            if result == 0:
                with self.lock:
                    self.open_ports.append(port)
                    print(f"Port {port}/tcp: OPEN")
                return True
        except Exception:
            pass
        return False
    
    def scan_port_syn(self, port):
        """SYN scan (-sS flag) - requires root privileges"""
        try:
            # Note: This is a simplified version. Real SYN scan requires raw sockets
            # and root privileges. For educational purposes, we'll use TCP connect
            return self.scan_port_tcp(port)
        except Exception:
            return False
    
    def get_service_version(self, port):
        """Service version detection (-sV flag)"""
        service_map = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S",
            3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL",
            1433: "MSSQL", 6379: "Redis", 27017: "MongoDB"
        }
        
        service = service_map.get(port, "Unknown")
        
        # Try to get banner for version detection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.ip, port))
            
            # Send HTTP request for web services
            if port in [80, 443, 8080, 8443]:
                sock.send(b"HEAD / HTTP/1.1\r\nHost: " + self.ip.encode() + b"\r\n\r\n")
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            if banner:
                # Extract version info from banner
                banner_lines = banner.split('\n')[0][:100]  # First line, max 100 chars
                return f"{service} ({banner_lines})"
        except:
            pass
        
        return service
    
    def worker_thread(self, port, scan_type, version_detection=False):
        """Worker thread for port scanning"""
        if scan_type == 'tcp':
            if self.scan_port_tcp(port):
                if version_detection:
                    service = self.get_service_version(port)
                    with self.lock:
                        print(f"Port {port}/tcp: OPEN - Service: {service}")
        elif scan_type == 'syn':
            if self.scan_port_syn(port):
                if version_detection:
                    service = self.get_service_version(port)
                    with self.lock:
                        print(f"Port {port}/tcp: OPEN - Service: {service}")
    
    def scan_ports(self, port_range, scan_type='tcp', version_detection=False):
        """Main scanning function with multithreading"""
        start_port, end_port = port_range
        
        print(f"\nStarting {scan_type.upper()} scan on {self.ip}")
        print(f"Scanning ports {start_port}-{end_port}")
        print(f"Time started: {datetime.now()}")
        print(f"Using {self.threads} threads")
        print("-" * 50)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for port in range(start_port, end_port + 1):
                future = executor.submit(self.worker_thread, port, scan_type, version_detection)
                futures.append(future)
            
            # Wait for all threads to complete
            for future in futures:
                future.result()
        
        end_time = time.time()
        
        print("-" * 50)
        print(f"Scan completed in {end_time - start_time:.2f} seconds")
        print(f"Found {len(self.open_ports)} open ports")
        
        if self.open_ports:
            print("\nOpen ports summary:")
            for port in sorted(self.open_ports):
                if version_detection:
                    service = self.get_service_version(port)
                    print(f"  {port}/tcp - {service}")
                else:
                    print(f"  {port}/tcp")

def main():
    # ASCII Banner
    banner = pyfiglet.figlet_format("PORT ZERO")
    print(banner)
    print("Enhanced Multi-threaded Port Scanner")
    print("Author: wangsa")
    print("-" * 50)
    
    # Argument parsing
    parser = argparse.ArgumentParser(description='Enhanced Port Scanner with nmap-like features')
    parser.add_argument('target', help='Target IP address or hostname')
    parser.add_argument('-p', '--ports', default='1-1000', 
                       help='Port range to scan (e.g., 1-1000, 80,443,22)')
    parser.add_argument('-t', '--threads', type=int, default=100,
                       help='Number of threads to use (default: 100)')
    parser.add_argument('-sS', '--syn-scan', action='store_true',
                       help='TCP SYN scan (requires root privileges)')
    parser.add_argument('-sV', '--version-scan', action='store_true',
                       help='Enable service version detection')
    parser.add_argument('-sn', '--ping-scan', action='store_true',
                       help='Ping scan only (no port scan)')
    
    # If no arguments provided, use interactive mode
    if len(sys.argv) == 1:
        target = input("Enter target IP or hostname: ")
        ports_input = input("Enter port range (e.g., 1-1000) [default: 1-1000]: ") or "1-1000"
        threads = int(input("Enter number of threads [default: 100]: ") or "100")
        
        args = argparse.Namespace(
            target=target,
            ports=ports_input,
            threads=threads,
            syn_scan=False,
            version_scan=False,
            ping_scan=False
        )
    else:
        args = parser.parse_args()
    
    # Initialize scanner
    scanner = PortScanner(args.target, args.threads)
    
    # Resolve target
    if not scanner.resolve_target():
        sys.exit(1)
    
    print(f"Target: {args.target} ({scanner.ip})")
    
    # Handle ping scan (-sn flag)
    if args.ping_scan:
        print("Performing ping scan...")
        if scanner.ping_host():
            print(f"Host {scanner.ip} is UP")
        else:
            print(f"Host {scanner.ip} appears to be DOWN")
        return
    
    # Parse port range
    try:
        if '-' in args.ports:
            start_port, end_port = map(int, args.ports.split('-'))
        elif ',' in args.ports:
            # Handle comma-separated ports
            ports_list = list(map(int, args.ports.split(',')))
            start_port, end_port = min(ports_list), max(ports_list)
            print("Note: Scanning range from minimum to maximum port in list")
        else:
            start_port = end_port = int(args.ports)
    except ValueError:
        print("Error: Invalid port range format")
        sys.exit(1)
    
    # Validate port range
    if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
        print("Error: Port numbers must be between 1 and 65535")
        sys.exit(1)
    
    if start_port > end_port:
        print("Error: Start port cannot be greater than end port")
        sys.exit(1)
    
    # Check if host is up before scanning
    if scanner.ping_host():
        print(f"Host {scanner.ip} is UP - proceeding with scan")
    else:
        print(f"Warning: Host {scanner.ip} appears to be DOWN")
        proceed = input("Continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            sys.exit(1)
    
    # Determine scan type
    scan_type = 'syn' if args.syn_scan else 'tcp'
    
    # Perform port scan
    try:
        scanner.scan_ports((start_port, end_port), scan_type, args.version_scan)
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
        print(f"Scanned ports so far: {len(scanner.open_ports)} open")
    except Exception as e:
        print(f"Error during scan: {e}")

if __name__ == "__main__":
    main()