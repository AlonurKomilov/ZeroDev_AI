#!/usr/bin/env python3
"""
Professional Port & Service Manager
Advanced port monitoring, cleanup, and service management
"""

import os
import re
import json
import time
import signal
import psutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/ZeroDev_AI/logs/port_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class PortInfo:
    """Information about a port and its service"""
    port: int
    protocol: str
    status: str
    pid: Optional[int]
    process_name: Optional[str]
    process_cmdline: Optional[str]
    connections: int
    bind_address: str
    service_type: str  # 'system', 'user', 'development', 'unknown'
    
@dataclass
class ServiceInfo:
    """Detailed service information"""
    name: str
    pid: int
    status: str
    cpu_percent: float
    memory_mb: float
    ports: List[int]
    start_time: str
    cmdline: str

@dataclass
class ProjectPortConfig:
    """Port configuration found in project files"""
    file_path: str
    line_number: int
    port: int
    context: str
    config_type: str  # 'hardcoded', 'env_var', 'config_file'

class ProfessionalPortManager:
    """Professional port and service management system"""
    
    def __init__(self, project_path: str = "/workspaces/ZeroDev_AI"):
        self.project_path = Path(project_path)
        self.known_services = {
            # Development services
            3000: "Next.js Development Server",
            3001: "React Development Server", 
            8000: "FastAPI/Django Development",
            8080: "HTTP Alternative Server",
            5000: "Flask Development Server",
            5173: "Vite Development Server",
            
            # Database services
            5432: "PostgreSQL",
            3306: "MySQL",
            6379: "Redis",
            27017: "MongoDB",
            
            # System services
            22: "SSH",
            53: "DNS",
            80: "HTTP",
            443: "HTTPS",
            2000: "Dev Container",
            2222: "Dev Container SSH"
        }
        
        # Ensure logs directory exists
        os.makedirs("/workspaces/ZeroDev_AI/logs", exist_ok=True)
        
    def scan_active_ports(self) -> List[PortInfo]:
        """Scan all active ports and their associated processes"""
        logger.info("Scanning active ports...")
        active_ports = []
        
        try:
            # Get network connections
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.status == psutil.CONN_LISTEN and conn.laddr:
                    port = conn.laddr.port
                    
                    # Get process info if available
                    process_name = None
                    process_cmdline = None
                    
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            process_name = process.name()
                            process_cmdline = ' '.join(process.cmdline())
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # Determine service type
                    service_type = self._classify_service(port, process_name, process_cmdline)
                    
                    port_info = PortInfo(
                        port=port,
                        protocol=conn.type.name if conn.type else "unknown",
                        status="LISTENING",
                        pid=conn.pid,
                        process_name=process_name,
                        process_cmdline=process_cmdline,
                        connections=1,
                        bind_address=conn.laddr.ip,
                        service_type=service_type
                    )
                    
                    active_ports.append(port_info)
                    
        except Exception as e:
            logger.error(f"Failed to scan ports: {e}")
            
        logger.info(f"Found {len(active_ports)} active ports")
        return active_ports
    
    def _classify_service(self, port: int, process_name: Optional[str], 
                         cmdline: Optional[str]) -> str:
        """Classify service type based on port and process info"""
        # System services (typically < 1024)
        if port < 1024:
            return "system"
            
        # Known development ports
        dev_ports = {3000, 3001, 8000, 8080, 5000, 5173, 4173, 9000}
        if port in dev_ports:
            return "development"
            
        # Check process name/command line for clues
        if process_name and cmdline:
            dev_indicators = ['node', 'python', 'uvicorn', 'next', 'vite', 'webpack']
            if any(indicator in process_name.lower() or 
                  indicator in cmdline.lower() for indicator in dev_indicators):
                return "development"
                
        # Database ports
        db_ports = {5432, 3306, 6379, 27017}
        if port in db_ports:
            return "database"
            
        return "user"
    
    def cleanup_unused_services(self, unused_services: List[PortInfo], 
                               force: bool = False) -> Dict[str, List[str]]:
        """Clean up unused services"""
        results = {
            "stopped": [],
            "failed": [],
            "skipped": []
        }
        
        for service in unused_services:
            if not service.pid:
                results["skipped"].append(f"Port {service.port}: No PID available")
                continue
                
            try:
                process = psutil.Process(service.pid)
                service_desc = f"Port {service.port} ({service.process_name}, PID {service.pid})"
                
                # Safety check - don't kill system processes
                if service.service_type == "system":
                    results["skipped"].append(f"{service_desc}: System service")
                    continue
                
                # Graceful shutdown first
                if not force:
                    logger.info(f"Sending TERM signal to {service_desc}")
                    process.terminate()
                    
                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        results["stopped"].append(f"{service_desc}: Gracefully terminated")
                        continue
                    except psutil.TimeoutExpired:
                        pass
                
                # Force kill if graceful shutdown failed or force=True
                logger.info(f"Force killing {service_desc}")
                process.kill()
                
                # Verify it's gone
                try:
                    process.wait(timeout=2)
                    results["stopped"].append(f"{service_desc}: Force killed")
                except psutil.TimeoutExpired:
                    results["failed"].append(f"{service_desc}: Could not kill process")
                    
            except psutil.NoSuchProcess:
                results["stopped"].append(f"Port {service.port}: Process already gone")
            except psutil.AccessDenied:
                results["failed"].append(f"Port {service.port}: Access denied")
            except Exception as e:
                results["failed"].append(f"Port {service.port}: {str(e)}")
                
        return results
    
    def kill_port(self, port: int, force: bool = False) -> bool:
        """Kill specific process using a port or clean phantom port states"""
        try:
            # First, find process using the port
            process_found = False
            for conn in psutil.net_connections(kind='inet'):
                if (conn.status == psutil.CONN_LISTEN and 
                    conn.laddr and conn.laddr.port == port and conn.pid):
                    
                    process = psutil.Process(conn.pid)
                    logger.info(f"Killing process on port {port}: {process.name()} (PID {conn.pid})")
                    
                    if force:
                        process.kill()
                    else:
                        process.terminate()
                        
                    # Wait for process to die
                    try:
                        process.wait(timeout=5)
                        return True
                    except psutil.TimeoutExpired:
                        if not force:
                            # Try force kill
                            process.kill()
                            process.wait(timeout=2)
                            return True
                    process_found = True
                    break
            
            # If no process found but port appears to be listening (phantom state)
            if not process_found:
                # Check if port shows up in netstat but has no PID
                phantom_found = False
                for conn in psutil.net_connections(kind='inet'):
                    if (conn.status == psutil.CONN_LISTEN and 
                        conn.laddr and conn.laddr.port == port and not conn.pid):
                        phantom_found = True
                        break
                
                if phantom_found:
                    logger.warning(f"Port {port} appears to be in phantom state (no process)")
                    # Try to clean phantom state using system tools
                    return self._clean_phantom_port(port)
                else:
                    logger.info(f"Port {port} is not currently in use")
                    return True
                            
        except Exception as e:
            logger.error(f"Failed to kill process on port {port}: {e}")
            
        return False
    
    def _clean_phantom_port(self, port: int) -> bool:
        """Attempt to clean phantom port states"""
        import subprocess
        
        try:
            # Method 1: Try to bind and immediately close the port (clears phantom state)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('127.0.0.1', port))
                sock.close()
                logger.info(f"Successfully cleared phantom state for port {port}")
                return True
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    logger.warning(f"Port {port} still appears to be in use after phantom cleanup")
                sock.close()
        except Exception as e:
            logger.error(f"Socket cleanup failed for port {port}: {e}")
        
        # Method 2: Use fuser if available (Linux)
        try:
            result = subprocess.run(['fuser', '-k', f'{port}/tcp'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"Used fuser to clean port {port}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        logger.warning(f"Could not clean phantom port {port} - may require system restart")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Professional Port & Service Manager")
    parser.add_argument("--scan", action="store_true", help="Scan active ports and services")
    parser.add_argument("--cleanup", action="store_true", help="Clean up unused services")
    parser.add_argument("--kill-port", type=int, help="Kill process on specific port")
    parser.add_argument("--force", action="store_true", help="Force kill processes")
    parser.add_argument("--project-path", type=str, default="/workspaces/ZeroDev_AI",
                       help="Project path to scan for configurations")
    
    args = parser.parse_args()
    
    try:
        manager = ProfessionalPortManager(args.project_path)
        
        if args.kill_port:
            success = manager.kill_port(args.kill_port, args.force)
            if success:
                print(f"✅ Successfully killed process on port {args.kill_port}")
                return 0
            else:
                print(f"❌ Failed to kill process on port {args.kill_port}")
                return 1
        
        # Default action: scan ports
        print("🔍 Scanning active ports and services...")
        active_ports = manager.scan_active_ports()
        
        # Print summary
        print("\n" + "="*70)
        print("🔌 PORT SCAN RESULTS")
        print("="*70)
        
        for port_info in active_ports:
            status_icon = "🟢" if port_info.service_type != "unknown" else "🟡"
            print(f"{status_icon} Port {port_info.port}: {port_info.process_name} ({port_info.service_type})")
            
        print(f"\n✅ Found {len(active_ports)} active ports")
        return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Port scan interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Port management failed: {e}")
        print(f"\n❌ Port management failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
