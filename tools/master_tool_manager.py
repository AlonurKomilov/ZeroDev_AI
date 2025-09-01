#!/usr/bin/env python3
"""
Professional ZeroDev AI Tool Manager
Master script to run all professional development tools
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class ProfessionalToolManager:
    """Manages all professional development tools"""
    
    def __init__(self):
        self.project_path = Path("/workspaces/ZeroDev_AI")
        self.tools_path = self.project_path / "tools"
        
        self.available_tools = {
            "emergency-verify": {
                "script": "professional_emergency_verifier.py",
                "description": "🛡️  Emergency panel verification and security audit",
                "args": []
            },
            "code-fix": {
                "script": "professional_ai_code_fixer.py", 
                "description": "🤖 AI-powered code quality fixer with Claude integration",
                "args": ["--category", "--apply", "--api-key"]
            },
            "port-manager": {
                "script": "professional_port_manager.py",
                "description": "🔌 Port scanning, monitoring, and cleanup",
                "args": ["--scan", "--cleanup", "--kill-port", "--force"]
            },
            "duplicate-cleaner": {
                "script": "professional_duplicate_cleaner.py",
                "description": "🗂️  Find and clean duplicate/similar files",
                "args": ["--clean", "--similarity"]
            }
        }
        
    def run_tool(self, tool_name: str, tool_args: List[str] = None) -> int:
        """Run a specific tool"""
        if tool_name not in self.available_tools:
            print(f"❌ Unknown tool: {tool_name}")
            return 1
            
        tool_info = self.available_tools[tool_name]
        script_path = self.tools_path / tool_info["script"]
        
        if not script_path.exists():
            print(f"❌ Tool script not found: {script_path}")
            return 1
            
        # Build command
        cmd = ["python", str(script_path)]
        if tool_args:
            cmd.extend(tool_args)
            
        print(f"🚀 Running {tool_info['description']}")
        print(f"📄 Command: {' '.join(cmd)}")
        print("-" * 60)
        
        try:
            result = subprocess.run(cmd, cwd=self.project_path)
            return result.returncode
        except KeyboardInterrupt:
            print("\n⚠️  Tool execution interrupted by user")
            return 130
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            return 1
    
    def run_all_tools(self, quick_scan: bool = False) -> Dict[str, int]:
        """Run all tools in sequence"""
        results = {}
        
        print("🎯 PROFESSIONAL DEVELOPMENT TOOLS - FULL SCAN")
        print("=" * 70)
        
        # Define tool execution order and default args
        execution_plan = [
            ("emergency-verify", []),
            ("port-manager", ["--scan"]),
            ("duplicate-cleaner", ["--similarity", "0.9"] if quick_scan else []),
            ("code-fix", ["--category", "security"] if quick_scan else ["--category", "all"])
        ]
        
        for tool_name, default_args in execution_plan:
            print(f"\n{'='*20} {tool_name.upper()} {'='*20}")
            
            try:
                exit_code = self.run_tool(tool_name, default_args)
                results[tool_name] = exit_code
                
                if exit_code == 0:
                    print(f"✅ {tool_name} completed successfully")
                else:
                    print(f"⚠️  {tool_name} completed with warnings/errors (code: {exit_code})")
                    
            except Exception as e:
                print(f"❌ {tool_name} failed: {e}")
                results[tool_name] = 1
                
        return results
    
    def show_tools_menu(self):
        """Interactive tools menu"""
        while True:
            print("\n" + "="*70)
            print("🎯 PROFESSIONAL ZERODEV AI TOOL MANAGER")
            print("="*70)
            
            print("\n📋 Available Tools:")
            for i, (tool_name, tool_info) in enumerate(self.available_tools.items(), 1):
                print(f"  {i}. {tool_name}: {tool_info['description']}")
                
            print(f"\n🔧 Quick Actions:")
            print(f"  A. Run All Tools (Full Scan)")
            print(f"  Q. Run All Tools (Quick Scan)")
            print(f"  X. Exit")
            
            choice = input("\n👉 Select option: ").strip().upper()
            
            if choice == 'X':
                print("👋 Goodbye!")
                break
            elif choice == 'A':
                print("\n🚀 Running full comprehensive scan...")
                results = self.run_all_tools(quick_scan=False)
                self.print_summary(results)
            elif choice == 'Q':
                print("\n⚡ Running quick scan...")
                results = self.run_all_tools(quick_scan=True)
                self.print_summary(results)
            elif choice.isdigit():
                tool_index = int(choice) - 1
                tool_names = list(self.available_tools.keys())
                
                if 0 <= tool_index < len(tool_names):
                    tool_name = tool_names[tool_index]
                    
                    # Get additional arguments
                    print(f"\n🔧 Available arguments for {tool_name}:")
                    available_args = self.available_tools[tool_name]["args"]
                    if available_args:
                        print(f"   {', '.join(available_args)}")
                    else:
                        print("   No additional arguments")
                        
                    extra_args = input("📝 Enter arguments (or press Enter for defaults): ").strip()
                    args = extra_args.split() if extra_args else []
                    
                    exit_code = self.run_tool(tool_name, args)
                    
                    if exit_code == 0:
                        print(f"\n✅ {tool_name} completed successfully!")
                    else:
                        print(f"\n⚠️  {tool_name} completed with exit code: {exit_code}")
                else:
                    print("❌ Invalid selection")
            else:
                print("❌ Invalid selection")
    
    def print_summary(self, results: Dict[str, int]):
        """Print execution summary"""
        print("\n" + "="*70)
        print("📊 EXECUTION SUMMARY")
        print("="*70)
        
        successful = 0
        with_issues = 0
        
        for tool_name, exit_code in results.items():
            status = "✅ SUCCESS" if exit_code == 0 else f"⚠️  WARNING ({exit_code})"
            print(f"  {tool_name:<20} {status}")
            
            if exit_code == 0:
                successful += 1
            else:
                with_issues += 1
                
        print(f"\n📈 Results: {successful} successful, {with_issues} with issues")
        
        if with_issues == 0:
            print("🎉 All tools completed successfully!")
        else:
            print("💡 Some tools reported issues - check individual reports for details")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Professional ZeroDev AI Tool Manager")
    parser.add_argument("tool", nargs="?", help="Tool to run (emergency-verify, code-fix, port-manager, duplicate-cleaner)")
    parser.add_argument("--all", action="store_true", help="Run all tools")
    parser.add_argument("--quick", action="store_true", help="Quick scan mode")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive menu")
    
    # Parse known args to allow tool-specific arguments
    args, unknown_args = parser.parse_known_args()
    
    manager = ProfessionalToolManager()
    
    try:
        if args.interactive:
            manager.show_tools_menu()
            return 0
        elif args.all:
            results = manager.run_all_tools(quick_scan=args.quick)
            manager.print_summary(results)
            
            # Exit with error if any tool failed
            failed_tools = [tool for tool, code in results.items() if code != 0]
            return 1 if failed_tools else 0
        elif args.tool:
            return manager.run_tool(args.tool, unknown_args)
        else:
            # Default to interactive menu
            manager.show_tools_menu()
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Tool manager interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Tool manager failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
