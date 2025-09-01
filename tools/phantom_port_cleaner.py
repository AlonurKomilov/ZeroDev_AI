#!/usr/bin/env python3
"""
Phantom Port Cleaner - Advanced tool to clean stale kernel socket states
"""

import socket
import subprocess
import psutil
import time
import sys
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class PhantomPortCleaner:
    """Advanced phantom port cleanup utility"""
    
    def __init__(self):
        self.phantom_ports = []
    
    def detect_phantom_ports(self) -> List[int]:
        """Detect ports that are listening but have no associated process"""
        phantom_ports = []
        
        logger.info("🔍 Scanning for phantom ports...")
        
        for conn in psutil.net_connections(kind='inet'):
            if (conn.status == psutil.CONN_LISTEN and 
                conn.laddr and not conn.pid):
                port = conn.laddr.port
                if port not in phantom_ports:
                    phantom_ports.append(port)
                    logger.warning(f"Found phantom port: {port}")
        
        self.phantom_ports = phantom_ports
        return phantom_ports
    
    def cleanup_method_socket_rebind(self, port: int) -> bool:
        """Method 1: Try to bind and release the port"""
        try:
            # Try both IPv4 and IPv6
            for family, addr in [(socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')]:
                try:
                    sock = socket.socket(family, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind((addr, port))
                    sock.close()
                    time.sleep(0.1)  # Give kernel time to clean up
                except OSError as e:
                    if e.errno != 98:  # Not "Address already in use"
                        logger.debug(f"Socket rebind failed for {family} on port {port}: {e}")
                    sock.close() if 'sock' in locals() else None
                    
            return True
        except Exception as e:
            logger.error(f"Socket rebind method failed for port {port}: {e}")
            return False
    
    def cleanup_method_fuser(self, port: int) -> bool:
        """Method 2: Use fuser command"""
        try:
            # Try TCP
            result = subprocess.run(['fuser', '-k', f'{port}/tcp'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"fuser successfully cleaned TCP port {port}")
                return True
            
            # Try UDP
            result = subprocess.run(['fuser', '-k', f'{port}/udp'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"fuser successfully cleaned UDP port {port}")
                return True
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.debug(f"fuser method failed for port {port}: {e}")
            
        return False
    
    def cleanup_method_netstat_kill(self, port: int) -> bool:
        """Method 3: Use netstat to find and kill connections"""
        try:
            # Get detailed connection info
            result = subprocess.run(['ss', '-tlnp', f'sport={port}'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if f':{port}' in line and 'LISTEN' in line:
                        logger.info(f"Found listening socket on port {port}: {line}")
                        
                        # Extract process info if available
                        if 'users:' in line:
                            # Process info found - this shouldn't happen for phantom ports
                            logger.warning(f"Port {port} has process info - not a phantom port")
                            return False
                        
            return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.debug(f"netstat kill method failed for port {port}: {e}")
            
        return False
    
    def cleanup_method_procfs_scan(self, port: int) -> bool:
        """Method 4: Scan /proc/net for socket states"""
        try:
            # Check /proc/net/tcp for IPv4
            with open('/proc/net/tcp', 'r') as f:
                for line in f.readlines()[1:]:  # Skip header
                    parts = line.strip().split()
                    if len(parts) >= 10:
                        local_addr = parts[1]
                        if ':' in local_addr:
                            addr_parts = local_addr.split(':')
                            if len(addr_parts) == 2:
                                port_hex = addr_parts[1]
                                port_dec = int(port_hex, 16)
                                if port_dec == port:
                                    state = parts[3]
                                    inode = parts[9]
                                    logger.info(f"Found port {port} in /proc/net/tcp - State: {state}, Inode: {inode}")
                                    
                                    # State 0A = LISTEN
                                    if state == '0A':
                                        logger.info(f"Port {port} is in LISTEN state in kernel")
                                        return True
            
            # Check /proc/net/tcp6 for IPv6
            try:
                with open('/proc/net/tcp6', 'r') as f:
                    for line in f.readlines()[1:]:
                        parts = line.strip().split()
                        if len(parts) >= 10:
                            local_addr = parts[1]
                            if ':' in local_addr:
                                addr_parts = local_addr.split(':')
                                if len(addr_parts) >= 2:
                                    port_hex = addr_parts[-1]  # Last part is port
                                    try:
                                        port_dec = int(port_hex, 16)
                                        if port_dec == port:
                                            logger.info(f"Found port {port} in /proc/net/tcp6")
                                            return True
                                    except ValueError:
                                        continue
            except FileNotFoundError:
                pass
                
        except Exception as e:
            logger.debug(f"procfs scan failed for port {port}: {e}")
            
        return False
    
    def clean_phantom_port(self, port: int) -> bool:
        """Clean a specific phantom port using multiple methods"""
        logger.info(f"🧹 Cleaning phantom port {port}...")
        
        methods = [
            ("Socket Rebind", self.cleanup_method_socket_rebind),
            ("Fuser Kill", self.cleanup_method_fuser),
            ("Netstat Analysis", self.cleanup_method_netstat_kill),
            ("ProcFS Scan", self.cleanup_method_procfs_scan)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"  Trying method: {method_name}")
                if method_func(port):
                    # Verify if port is still phantom
                    time.sleep(0.5)
                    if not self._is_port_phantom(port):
                        logger.info(f"✅ Port {port} successfully cleaned using {method_name}")
                        return True
                    else:
                        logger.info(f"  Method {method_name} completed but port still phantom")
            except Exception as e:
                logger.error(f"  Method {method_name} failed: {e}")
        
        logger.warning(f"❌ Could not clean phantom port {port}")
        return False
    
    def _is_port_phantom(self, port: int) -> bool:
        """Check if a port is still in phantom state"""
        for conn in psutil.net_connections(kind='inet'):
            if (conn.status == psutil.CONN_LISTEN and 
                conn.laddr and conn.laddr.port == port and not conn.pid):
                return True
        return False
    
    def clean_all_phantoms(self) -> Tuple[int, int]:
        """Clean all detected phantom ports"""
        phantom_ports = self.detect_phantom_ports()
        
        if not phantom_ports:
            logger.info("✅ No phantom ports detected!")
            return 0, 0
        
        logger.info(f"Found {len(phantom_ports)} phantom ports: {phantom_ports}")
        
        cleaned = 0
        failed = 0
        
        for port in phantom_ports:
            if self.clean_phantom_port(port):
                cleaned += 1
            else:
                failed += 1
        
        logger.info(f"📊 Cleanup Results: {cleaned} cleaned, {failed} failed")
        return cleaned, failed

def main():
    """Main function"""
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            cleaner = PhantomPortCleaner()
            success = cleaner.clean_phantom_port(port)
            sys.exit(0 if success else 1)
        except ValueError:
            logger.error("Invalid port number")
            sys.exit(1)
    else:
        # Clean all phantom ports
        cleaner = PhantomPortCleaner()
        cleaned, failed = cleaner.clean_all_phantoms()
        sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
