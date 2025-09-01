#!/usr/bin/env python3
"""
Performance Optimization Script for ZeroDev AI
Analyzes and optimizes various performance aspects of the application
"""

import os
import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import psutil
import subprocess

class PerformanceOptimizer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_system_resources(self) -> Dict[str, Any]:
        """Check current system resource usage"""
        self.log("Checking system resources...")
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            "cpu_usage": cpu_percent,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_free": disk.free,
            "disk_percent": (disk.used / disk.total) * 100
        }
        
        self.log(f"CPU Usage: {cpu_percent}%")
        self.log(f"Memory Usage: {memory.percent}%")
        self.log(f"Disk Usage: {resources['disk_percent']:.1f}%")
        
        return resources
        
    def analyze_docker_performance(self) -> Dict[str, Any]:
        """Analyze Docker container performance"""
        self.log("Analyzing Docker performance...")
        
        try:
            # Check if Docker is running
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": "Docker not running or not accessible"}
                
            # Get container stats
            stats_result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
                capture_output=True, text=True
            )
            
            containers = []
            if stats_result.returncode == 0:
                lines = stats_result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            containers.append({
                                "name": parts[0],
                                "cpu": parts[1],
                                "memory": parts[2]
                            })
                            
            return {"containers": containers}
            
        except Exception as e:
            return {"error": str(e)}
            
    def check_database_performance(self) -> Dict[str, Any]:
        """Check database connection and performance"""
        self.log("Checking database performance...")
        
        # For now, return basic check
        # In real implementation, you'd connect to PostgreSQL and run performance queries
        return {
            "status": "mock_check",
            "connection_time": "< 100ms",
            "query_performance": "good"
        }
        
    def analyze_frontend_build(self) -> Dict[str, Any]:
        """Analyze frontend build performance"""
        self.log("Analyzing frontend build...")
        
        frontend_path = self.project_root / "frontend"
        if not frontend_path.exists():
            return {"error": "Frontend directory not found"}
            
        try:
            # Check package.json size and dependencies
            package_json_path = frontend_path / "package.json"
            if package_json_path.exists():
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    
                deps_count = len(package_data.get('dependencies', {}))
                dev_deps_count = len(package_data.get('devDependencies', {}))
                
                return {
                    "dependencies_count": deps_count,
                    "dev_dependencies_count": dev_deps_count,
                    "total_dependencies": deps_count + dev_deps_count
                }
            else:
                return {"error": "package.json not found"}
                
        except Exception as e:
            return {"error": str(e)}
            
    def check_python_performance(self) -> Dict[str, Any]:
        """Check Python backend performance"""
        self.log("Checking Python backend performance...")
        
        backend_path = self.project_root / "backend"
        if not backend_path.exists():
            return {"error": "Backend directory not found"}
            
        try:
            # Count Python files
            py_files = list(backend_path.rglob("*.py"))
            
            # Check requirements.txt
            req_path = backend_path / "requirements.txt"
            req_count = 0
            if req_path.exists():
                with open(req_path, 'r') as f:
                    req_count = len([line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')])
                    
            return {
                "python_files_count": len(py_files),
                "requirements_count": req_count,
                "status": "analyzed"
            }
            
        except Exception as e:
            return {"error": str(e)}
            
    def optimize_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on analysis"""
        suggestions = []
        
        # System resource suggestions
        if self.results.get('system_resources'):
            resources = self.results['system_resources']
            if resources.get('memory_percent', 0) > 80:
                suggestions.append("🔍 HIGH MEMORY USAGE: Consider increasing system memory or optimizing application memory usage")
            if resources.get('cpu_usage', 0) > 80:
                suggestions.append("🔍 HIGH CPU USAGE: Consider optimizing CPU-intensive operations")
            if resources.get('disk_percent', 0) > 90:
                suggestions.append("🔍 LOW DISK SPACE: Clean up unnecessary files and logs")
                
        # Frontend suggestions
        if self.results.get('frontend_build'):
            frontend = self.results['frontend_build']
            if frontend.get('total_dependencies', 0) > 100:
                suggestions.append("📦 LARGE DEPENDENCY COUNT: Review and remove unused dependencies")
                
        # Docker suggestions
        if self.results.get('docker_performance', {}).get('containers'):
            suggestions.append("🐳 DOCKER OPTIMIZATION: Consider multi-stage builds and layer caching")
            
        # General suggestions
        suggestions.extend([
            "⚡ Enable Redis caching for frequently accessed data",
            "🗜️ Implement gzip compression for API responses",
            "📊 Add application monitoring with metrics collection",
            "🔄 Implement database connection pooling",
            "🎯 Use CDN for static assets in production"
        ])
        
        return suggestions
        
    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        report = f"""
# 🚀 ZeroDev AI Performance Optimization Report

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}

## 📊 System Resources
"""
        
        if 'system_resources' in self.results:
            resources = self.results['system_resources']
            report += f"""
- **CPU Usage:** {resources.get('cpu_usage', 'N/A')}%
- **Memory Usage:** {resources.get('memory_percent', 'N/A')}%
- **Disk Usage:** {resources.get('disk_percent', 'N/A'):.1f}%
- **Available Memory:** {resources.get('memory_available', 0) / (1024**3):.1f} GB
"""

        if 'docker_performance' in self.results:
            report += f"""
## 🐳 Docker Performance
"""
            docker_data = self.results['docker_performance']
            if 'containers' in docker_data:
                for container in docker_data['containers']:
                    report += f"- **{container['name']}:** CPU {container['cpu']}, Memory {container['memory']}\n"
            elif 'error' in docker_data:
                report += f"- Error: {docker_data['error']}\n"

        if 'frontend_build' in self.results:
            frontend = self.results['frontend_build']
            report += f"""
## 🎨 Frontend Analysis
- **Dependencies:** {frontend.get('dependencies_count', 'N/A')}
- **Dev Dependencies:** {frontend.get('dev_dependencies_count', 'N/A')}
- **Total:** {frontend.get('total_dependencies', 'N/A')}
"""

        if 'python_performance' in self.results:
            python_data = self.results['python_performance']
            report += f"""
## 🐍 Python Backend Analysis
- **Python Files:** {python_data.get('python_files_count', 'N/A')}
- **Requirements:** {python_data.get('requirements_count', 'N/A')}
"""

        # Add suggestions
        suggestions = self.optimize_suggestions()
        if suggestions:
            report += "\n## 🎯 Optimization Suggestions\n\n"
            for suggestion in suggestions:
                report += f"- {suggestion}\n"
                
        return report
        
    async def run_analysis(self) -> str:
        """Run complete performance analysis"""
        self.log("🚀 Starting ZeroDev AI Performance Analysis")
        
        # Run all checks
        self.results['system_resources'] = self.check_system_resources()
        self.results['docker_performance'] = self.analyze_docker_performance()
        self.results['database_performance'] = self.check_database_performance()
        self.results['frontend_build'] = self.analyze_frontend_build()
        self.results['python_performance'] = self.check_python_performance()
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        report_path = self.project_root / "reports" / f"performance_analysis_{time.strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write(report)
            
        self.log(f"📊 Performance report saved to: {report_path}")
        self.log("✅ Performance analysis complete!")
        
        return str(report_path)

async def main():
    """Main entry point"""
    optimizer = PerformanceOptimizer()
    report_path = await optimizer.run_analysis()
    print(f"\n📊 Performance analysis complete! Report saved to: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
