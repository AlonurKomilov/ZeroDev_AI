#!/usr/bin/env python3
"""
Professional AI-powered Code Quality Fixer
Advanced code analysis and automated fixing using Claude 3.5 Sonnet
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/ZeroDev_AI/logs/code_fixer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not available, using system environment variables")

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.warning("Anthropic library not available. Install with: pip install anthropic")

@dataclass 
class CodeIssue:
    """Represents a code quality issue"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    message: str
    suggested_fix: Optional[str] = None
    
@dataclass
class FixResult:
    """Result of applying a fix"""
    success: bool
    file_path: str
    lines_changed: int
    fix_description: str
    errors: List[str]

@dataclass
class AnalysisReport:
    """Complete analysis report"""
    timestamp: str
    project_path: str
    total_files: int
    issues_found: List[CodeIssue]
    fixes_applied: List[FixResult]
    security_score: int
    performance_score: int
    maintainability_score: int
    recommendations: List[str]

# Professional automated fixes configuration
PROFESSIONAL_FIXES = {
    "security": {
        "tools": [
            ["bandit", "-r", ".", "-f", "json", "-o", "security-report.json"],
            ["safety", "check", "--json", "--output", "safety-report.json"],
            ["semgrep", "--config=auto", "--json", "--output=semgrep-report.json", "."]
        ],
        "ruff_rules": "S"  # Security rules
    },
    "performance": {
        "tools": [
            ["pyupgrade", "--py311-plus"],
            ["ruff", "check", "--select", "PERF,UP,B", "--fix", "."]
        ],
        "ruff_rules": "PERF,UP,B"
    },
    "style": {
        "tools": [
            ["black", ".", "--line-length=88"],
            ["isort", ".", "--profile=black", "--line-length=88"],
            ["ruff", "format", "."],
            ["ruff", "check", "--select", "E,W,F", "--fix", "."]
        ],
        "ruff_rules": "E,W,F"
    },
    "imports": {
        "tools": [
            ["autoflake", "--remove-all-unused-imports", "--remove-unused-variables", 
             "--in-place", "--recursive", ".", "--exclude=__pycache__,*.pyc,.git"],
            ["ruff", "check", "--select", "I,F401", "--fix", "."]
        ],
        "ruff_rules": "I,F401"
    },
    "complexity": {
        "tools": [
            ["ruff", "check", "--select", "C90,PLR", "--fix", "."]
        ],
        "ruff_rules": "C90,PLR"
    },
    "type-safety": {
        "tools": [
            ["mypy", ".", "--ignore-missing-imports", "--install-types", "--non-interactive"],
            ["ruff", "check", "--select", "ANN", "--fix", "."]
        ],
        "ruff_rules": "ANN"
    }
}

class ProfessionalCodeFixer:
    """Professional-grade code quality fixer with AI integration"""
    
    def __init__(self, project_path: str = ".", api_key: str = None, config_file: str = None):
        self.project_path = Path(project_path).resolve()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.config = self._load_config(config_file)
        
        # Ensure logs directory exists
        os.makedirs("/workspaces/ZeroDev_AI/logs", exist_ok=True)
        
        if self.api_key and HAS_ANTHROPIC:
            self.client = Anthropic(api_key=self.api_key)
            logger.info("AI client initialized successfully")
        else:
            logger.warning("AI client not available - will use automated fixes only")
            
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "max_file_size": 1024 * 1024,  # 1MB
            "excluded_dirs": [".git", "__pycache__", ".pytest_cache", "node_modules"],
            "included_extensions": [".py", ".pyi"],
            "severity_levels": ["error", "warning", "info"],
            "ai_model": "claude-3-5-haiku-20241022",
            "max_fixes_per_file": 10
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                default_config.update(custom_config)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
                
        return default_config
    
    def run_command_safely(self, cmd: List[str], timeout: int = 300, 
                          capture_output: bool = True) -> Tuple[int, str, str]:
        """Execute command with proper error handling and timeout"""
        try:
            cmd_str = " ".join(cmd)
            logger.debug(f"Executing command: {cmd_str}")
            
            if capture_output:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout,
                    cwd=self.project_path
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, timeout=timeout, cwd=self.project_path)
                return result.returncode, "", ""
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {cmd_str}")
            return 1, "", f"Command timed out after {timeout}s"
        except FileNotFoundError:
            logger.error(f"Command not found: {cmd[0]}")
            return 127, "", f"Command not found: {cmd[0]}"
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return 1, "", str(e)
    
    def discover_python_files(self) -> List[Path]:
        """Discover all Python files in the project"""
        python_files = []
        
        for ext in self.config["included_extensions"]:
            pattern = f"**/*{ext}"
            files = self.project_path.glob(pattern)
            
            for file_path in files:
                # Skip excluded directories
                if any(excluded in str(file_path) for excluded in self.config["excluded_dirs"]):
                    continue
                    
                # Skip files that are too large
                try:
                    if file_path.stat().st_size > self.config["max_file_size"]:
                        logger.warning(f"Skipping large file: {file_path}")
                        continue
                except OSError:
                    continue
                    
                python_files.append(file_path)
                
        logger.info(f"Discovered {len(python_files)} Python files")
        return python_files
    
    def analyze_with_ruff(self, fix_category: str = "all") -> List[CodeIssue]:
        """Analyze code using Ruff linter"""
        issues = []
        
        if fix_category == "all":
            rules = ",".join([config["ruff_rules"] for config in PROFESSIONAL_FIXES.values()])
        else:
            rules = PROFESSIONAL_FIXES.get(fix_category, {}).get("ruff_rules", "ALL")
            
        cmd = ["ruff", "check", "--select", rules, "--format", "json", "."]
        
        exit_code, stdout, stderr = self.run_command_safely(cmd)
        
        if stdout:
            try:
                ruff_results = json.loads(stdout)
                
                for result in ruff_results:
                    issue = CodeIssue(
                        file_path=result.get("filename", ""),
                        line_number=result.get("location", {}).get("row", 0),
                        issue_type=result.get("code", ""),
                        severity=self._map_ruff_severity(result.get("code", "")),
                        message=result.get("message", ""),
                        suggested_fix=result.get("fix", {}).get("message") if result.get("fix") else None
                    )
                    issues.append(issue)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Ruff output: {e}")
                
        return issues
    
    def _map_ruff_severity(self, code: str) -> str:
        """Map Ruff error codes to severity levels"""
        if code.startswith(('E', 'W')):
            return "warning"
        elif code.startswith(('F', 'S')):
            return "error"
        elif code.startswith(('C', 'N')):
            return "info"
        else:
            return "warning"
    
    def analyze_with_mypy(self) -> List[CodeIssue]:
        """Analyze code with MyPy for type issues"""
        issues = []
        
        cmd = ["mypy", ".", "--ignore-missing-imports", "--show-error-codes", "--no-error-summary"]
        exit_code, stdout, stderr = self.run_command_safely(cmd)
        
        if stdout:
            for line in stdout.split('\n'):
                if ':' in line and 'error:' in line:
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        file_path = parts[0].strip()
                        try:
                            line_number = int(parts[1].strip())
                        except ValueError:
                            line_number = 0
                            
                        message = parts[3].strip() if len(parts) > 3 else ""
                        
                        issue = CodeIssue(
                            file_path=file_path,
                            line_number=line_number,
                            issue_type="mypy",
                            severity="error",
                            message=message
                        )
                        issues.append(issue)
                        
        return issues
    
    def analyze_security_with_bandit(self) -> List[CodeIssue]:
        """Security analysis with Bandit"""
        issues = []
        
        cmd = ["bandit", "-r", ".", "-f", "json"]
        exit_code, stdout, stderr = self.run_command_safely(cmd)
        
        if stdout:
            try:
                bandit_results = json.loads(stdout)
                
                for result in bandit_results.get("results", []):
                    issue = CodeIssue(
                        file_path=result.get("filename", ""),
                        line_number=result.get("line_number", 0),
                        issue_type=result.get("test_id", ""),
                        severity=result.get("issue_severity", "").lower(),
                        message=result.get("issue_text", "")
                    )
                    issues.append(issue)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Bandit output: {e}")
                
        return issues
    
    def apply_automated_fixes(self, fix_category: str = "all") -> Dict[str, List[FixResult]]:
        """Apply automated code fixes"""
        results = {}
        
        categories = PROFESSIONAL_FIXES.keys() if fix_category == "all" else [fix_category]
        
        for category in categories:
            if category not in PROFESSIONAL_FIXES:
                logger.warning(f"Unknown fix category: {category}")
                continue
                
            logger.info(f"Applying {category} fixes...")
            category_results = []
            
            tools = PROFESSIONAL_FIXES[category]["tools"]
            
            for tool_cmd in tools:
                tool_name = tool_cmd[0]
                logger.debug(f"Running {tool_name}: {' '.join(tool_cmd)}")
                
                exit_code, stdout, stderr = self.run_command_safely(tool_cmd)
                
                fix_result = FixResult(
                    success=exit_code == 0,
                    file_path=str(self.project_path),
                    lines_changed=0,  # Would need git diff to calculate
                    fix_description=f"{tool_name} execution",
                    errors=[stderr] if stderr and exit_code != 0 else []
                )
                
                category_results.append(fix_result)
                
                if exit_code == 0:
                    logger.debug(f"✅ {tool_name} completed successfully")
                else:
                    logger.warning(f"⚠️ {tool_name} completed with warnings/errors")
                    
            results[category] = category_results
            
        return results
    
    async def get_ai_analysis(self, issues: List[CodeIssue], context: str = "") -> Optional[str]:
        """Get AI analysis and suggestions"""
        if not self.client:
            logger.warning("AI client not available")
            return None
            
        # Limit issues to avoid token limits
        limited_issues = issues[:20]
        
        prompt = self._create_ai_prompt(limited_issues, context)
        
        try:
            logger.info("Requesting AI analysis...")
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.config["ai_model"],
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text if response.content else None
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def _create_ai_prompt(self, issues: List[CodeIssue], context: str) -> str:
        """Create AI prompt for code analysis"""
        prompt = f"""You are a senior Python developer performing a code quality review.

Project Context: {context}

I need you to analyze these code issues and provide specific fixes:

=== CODE ISSUES ===
"""
        
        for i, issue in enumerate(issues, 1):
            prompt += f"""
Issue {i}:
- File: {issue.file_path}
- Line: {issue.line_number}
- Type: {issue.issue_type}
- Severity: {issue.severity}
- Message: {issue.message}
"""

        prompt += """
=== REQUIREMENTS ===
For each critical issue, provide:
1. Root cause analysis
2. Specific fix with exact code
3. Why this fix improves code quality
4. Alternative approaches if applicable

Focus on:
- Security vulnerabilities
- Performance bottlenecks  
- Maintainability improvements
- Type safety enhancements

Provide fixes in this format:
```
ISSUE: [Issue number]
FILE: [file path]
LINE: [line number]
PROBLEM: [detailed explanation]
SOLUTION: [exact code fix]
RATIONALE: [why this fix is better]
IMPACT: [what this improves]
```

Prioritize fixes by impact and criticality.
"""
        
        return prompt
    
    def calculate_quality_scores(self, issues: List[CodeIssue]) -> Tuple[int, int, int]:
        """Calculate quality scores based on issues found"""
        security_score = 100
        performance_score = 100
        maintainability_score = 100
        
        for issue in issues:
            severity_weight = {"error": 5, "warning": 2, "info": 1}
            weight = severity_weight.get(issue.severity, 1)
            
            if issue.issue_type.startswith('S'):  # Security issues
                security_score -= weight
            elif issue.issue_type.startswith(('PERF', 'UP', 'B')):  # Performance
                performance_score -= weight
            else:  # General maintainability
                maintainability_score -= weight
                
        return (
            max(0, security_score),
            max(0, performance_score), 
            max(0, maintainability_score)
        )
    
    async def comprehensive_analysis(self, fix_category: str = "all", 
                                   apply_fixes: bool = False) -> AnalysisReport:
        """Perform comprehensive code analysis"""
        start_time = time.time()
        logger.info("Starting comprehensive code analysis...")
        
        # Discover files
        python_files = self.discover_python_files()
        
        # Collect all issues
        all_issues = []
        
        # Ruff analysis
        logger.info("Running Ruff analysis...")
        ruff_issues = self.analyze_with_ruff(fix_category)
        all_issues.extend(ruff_issues)
        
        # MyPy analysis
        logger.info("Running MyPy analysis...")
        mypy_issues = self.analyze_with_mypy()
        all_issues.extend(mypy_issues)
        
        # Security analysis
        if fix_category in ["all", "security"]:
            logger.info("Running Bandit security analysis...")
            security_issues = self.analyze_security_with_bandit()
            all_issues.extend(security_issues)
        
        # Apply fixes if requested
        fixes_applied = []
        if apply_fixes:
            logger.info("Applying automated fixes...")
            fix_results = self.apply_automated_fixes(fix_category)
            for category_fixes in fix_results.values():
                fixes_applied.extend(category_fixes)
        
        # Calculate quality scores
        security_score, performance_score, maintainability_score = self.calculate_quality_scores(all_issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues)
        
        # Get AI analysis if available
        ai_context = f"Python project with {len(python_files)} files"
        ai_analysis = await self.get_ai_analysis(all_issues, ai_context)
        
        if ai_analysis:
            recommendations.append("AI Analysis Available - See detailed report")
        
        analysis_time = time.time() - start_time
        logger.info(f"Analysis completed in {analysis_time:.2f} seconds")
        
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            project_path=str(self.project_path),
            total_files=len(python_files),
            issues_found=all_issues,
            fixes_applied=fixes_applied,
            security_score=security_score,
            performance_score=performance_score,
            maintainability_score=maintainability_score,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, issues: List[CodeIssue]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        issue_counts = {}
        for issue in issues:
            issue_type = issue.issue_type.split('.')[0] if '.' in issue.issue_type else issue.issue_type
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Generate recommendations based on most common issues
        if issue_counts.get('F401', 0) > 5:
            recommendations.append("High number of unused imports - consider using automated import cleaners")
            
        if issue_counts.get('E501', 0) > 10:
            recommendations.append("Many line length violations - configure code formatter")
            
        if any(code.startswith('S') for code in issue_counts.keys()):
            recommendations.append("Security issues detected - review and fix immediately")
            
        if issue_counts.get('C901', 0) > 0:
            recommendations.append("Complex functions detected - consider refactoring")
            
        return recommendations
    
    def save_report(self, report: AnalysisReport, output_path: str = None) -> str:
        """Save analysis report to file"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/workspaces/ZeroDev_AI/reports/code_analysis_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
            
        logger.info(f"Analysis report saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Professional AI-powered Code Quality Fixer")
    parser.add_argument("--path", type=str, default=".", help="Project path to analyze")
    parser.add_argument("--category", choices=["all"] + list(PROFESSIONAL_FIXES.keys()), 
                       default="all", help="Category of fixes to apply")
    parser.add_argument("--apply", action="store_true", help="Apply automated fixes")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--output", type=str, help="Output report path")
    parser.add_argument("--api-key", type=str, help="Anthropic API key")
    
    args = parser.parse_args()
    
    try:
        fixer = ProfessionalCodeFixer(
            project_path=args.path,
            api_key=args.api_key,
            config_file=args.config
        )
        
        # Run analysis
        loop = asyncio.get_event_loop()
        report = loop.run_until_complete(
            fixer.comprehensive_analysis(
                fix_category=args.category,
                apply_fixes=args.apply
            )
        )
        
        # Save report
        report_path = fixer.save_report(report, args.output)
        
        # Print summary
        print("\n" + "="*70)
        print("🎯 PROFESSIONAL CODE QUALITY ANALYSIS REPORT")
        print("="*70)
        
        print(f"\n📊 Project Analysis Summary:")
        print(f"   📁 Files Analyzed: {report.total_files}")
        print(f"   🐛 Issues Found: {len(report.issues_found)}")
        print(f"   🔧 Fixes Applied: {len(report.fixes_applied)}")
        
        print(f"\n📈 Quality Scores:")
        print(f"   🔒 Security: {report.security_score}/100")
        print(f"   ⚡ Performance: {report.performance_score}/100")
        print(f"   🛠️  Maintainability: {report.maintainability_score}/100")
        
        if report.issues_found:
            print(f"\n🔍 Top Issues by Type:")
            issue_types = {}
            for issue in report.issues_found:
                issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
            
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {issue_type}: {count} occurrences")
        
        if report.recommendations:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📄 Detailed report: {report_path}")
        
        # Exit code based on critical issues
        critical_issues = [i for i in report.issues_found if i.severity == "error"]
        exit_code = 1 if critical_issues else 0
        
        if critical_issues:
            print(f"\n⚠️  Found {len(critical_issues)} critical issues - fix required")
        else:
            print(f"\n✅ No critical issues found - code quality looks good!")
            
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\n❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
