#!/usr/bin/env python3
"""
Professional Emergency Panel Verifier
Advanced HTML/CSS/JS verification without external dependencies
"""

import os
import re
import json
import time
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/ZeroDev_AI/logs/emergency_verifier.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class FileAnalysis:
    """Data class for file analysis results"""
    path: str
    size: int
    hash: str
    mime_type: str
    encoding: str
    lines: int
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

@dataclass
class SecurityCheck:
    """Security analysis results"""
    file_path: str
    vulnerabilities: List[str]
    security_score: int
    recommendations: List[str]

class HTMLValidator(HTMLParser):
    """Custom HTML parser for validation"""
    
    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.tags = []
        self.attributes = {}
        self.links = []
        self.scripts = []
        self.styles = []
        
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attr_dict = dict(attrs)
        
        # Check for security issues
        if tag == 'script':
            src = attr_dict.get('src', '')
            if src:
                self.scripts.append(src)
                # Check for external scripts
                if src.startswith(('http://', 'https://', '//')):
                    self.warnings.append(f"External script detected: {src}")
                    
        elif tag == 'link':
            href = attr_dict.get('href', '')
            rel = attr_dict.get('rel', '')
            if href and rel == 'stylesheet':
                self.styles.append(href)
                
        elif tag == 'a':
            href = attr_dict.get('href', '')
            if href:
                self.links.append(href)
                
        # Check for inline event handlers (security risk)
        for attr, value in attrs:
            if attr.startswith('on'):
                self.warnings.append(f"Inline event handler found: {attr}='{value}'")
                
    def handle_data(self, data):
        # Check for suspicious content
        suspicious_patterns = [
            r'eval\s*\(',
            r'document\.write\s*\(',
            r'innerHTML\s*=',
            r'outerHTML\s*='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                self.warnings.append(f"Potentially unsafe JavaScript pattern: {pattern}")

class ProfessionalEmergencyVerifier:
    """Professional-grade emergency panel verification system"""
    
    def __init__(self, base_path: str = "/workspaces/ZeroDev_AI/emergency-panel-app"):
        self.base_path = Path(base_path)
        self.results = {}
        self.security_issues = []
        self.performance_metrics = {}
        
        # Create logs directory if it doesn't exist
        os.makedirs("/workspaces/ZeroDev_AI/logs", exist_ok=True)
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        try:
            # Try common encodings
            encodings = ['utf-8', 'utf-16', 'ascii', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(100)  # Read first 100 chars
                    return encoding
                except UnicodeDecodeError:
                    continue
                    
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def analyze_html_file(self, file_path: Path) -> FileAnalysis:
        """Comprehensive HTML file analysis"""
        errors = []
        warnings = []
        metadata = {}
        
        try:
            encoding = self.detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            lines = len(content.splitlines())
            
            # Parse HTML
            parser = HTMLValidator()
            try:
                parser.feed(content)
                warnings.extend(parser.warnings)
                metadata.update({
                    'tags_count': len(parser.tags),
                    'unique_tags': len(set(parser.tags)),
                    'scripts': parser.scripts,
                    'styles': parser.styles,
                    'links': parser.links
                })
            except Exception as e:
                errors.append(f"HTML parsing error: {str(e)}")
                
            # Check for required elements
            required_elements = ['html', 'head', 'body', 'title']
            for element in required_elements:
                if f'<{element}' not in content.lower():
                    warnings.append(f"Missing required HTML element: {element}")
                    
            # Check for doctype
            if not content.strip().lower().startswith('<!doctype'):
                warnings.append("Missing DOCTYPE declaration")
                
            # Check for responsive design
            if 'viewport' not in content.lower():
                warnings.append("Missing viewport meta tag for mobile responsiveness")
                
            # Performance checks
            script_count = content.lower().count('<script')
            if script_count > 10:
                warnings.append(f"High number of scripts ({script_count}) may impact performance")
                
            return FileAnalysis(
                path=str(file_path),
                size=file_path.stat().st_size,
                hash=self.calculate_file_hash(file_path),
                mime_type=mimetypes.guess_type(str(file_path))[0] or 'text/html',
                encoding=encoding,
                lines=lines,
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze HTML file {file_path}: {e}")
            return FileAnalysis(
                path=str(file_path),
                size=0,
                hash="",
                mime_type="unknown",
                encoding="unknown",
                lines=0,
                valid=False,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
    
    def analyze_js_file(self, file_path: Path) -> FileAnalysis:
        """Analyze JavaScript file for security and quality"""
        errors = []
        warnings = []
        metadata = {}
        
        try:
            encoding = self.detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            lines = len(content.splitlines())
            
            # Security checks
            security_patterns = [
                (r'eval\s*\(', 'Use of eval() is dangerous'),
                (r'document\.write\s*\(', 'document.write can be unsafe'),
                (r'innerHTML\s*=', 'innerHTML assignment can lead to XSS'),
                (r'\.src\s*=\s*[\'"]javascript:', 'JavaScript URL scheme detected'),
                (r'window\.location\s*=', 'Direct location assignment can be unsafe'),
            ]
            
            for pattern, message in security_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    warnings.append(f"{message} - Found {len(matches)} occurrences")
                    
            # Code quality checks
            if 'console.log' in content:
                warnings.append("Console.log statements found - remove in production")
                
            if 'debugger' in content:
                warnings.append("Debugger statements found - remove in production")
                
            # Count functions and variables
            function_count = len(re.findall(r'function\s+\w+', content))
            var_count = len(re.findall(r'\b(var|let|const)\s+\w+', content))
            
            metadata.update({
                'function_count': function_count,
                'variable_count': var_count,
                'minified': '\n' not in content[:1000] and len(content) > 500
            })
            
            return FileAnalysis(
                path=str(file_path),
                size=file_path.stat().st_size,
                hash=self.calculate_file_hash(file_path),
                mime_type='application/javascript',
                encoding=encoding,
                lines=lines,
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze JS file {file_path}: {e}")
            return FileAnalysis(
                path=str(file_path),
                size=0,
                hash="",
                mime_type="unknown",
                encoding="unknown",
                lines=0,
                valid=False,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
    
    def analyze_css_file(self, file_path: Path) -> FileAnalysis:
        """Analyze CSS file"""
        errors = []
        warnings = []
        metadata = {}
        
        try:
            encoding = self.detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            lines = len(content.splitlines())
            
            # Basic CSS validation
            # Count selectors, rules, and properties
            selector_count = len(re.findall(r'[^{}]+\s*\{', content))
            property_count = len(re.findall(r'[^:]+\s*:\s*[^;]+;', content))
            
            # Check for common issues
            if '@import' in content:
                warnings.append("@import statements can impact performance")
                
            if '!important' in content:
                important_count = content.count('!important')
                warnings.append(f"Found {important_count} !important declarations - use sparingly")
                
            metadata.update({
                'selector_count': selector_count,
                'property_count': property_count,
                'minified': '\n' not in content[:1000] and len(content) > 500
            })
            
            return FileAnalysis(
                path=str(file_path),
                size=file_path.stat().st_size,
                hash=self.calculate_file_hash(file_path),
                mime_type='text/css',
                encoding=encoding,
                lines=lines,
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze CSS file {file_path}: {e}")
            return FileAnalysis(
                path=str(file_path),
                size=0,
                hash="",
                mime_type="unknown", 
                encoding="unknown",
                lines=0,
                valid=False,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
    
    def security_audit(self, file_analysis: FileAnalysis) -> SecurityCheck:
        """Perform security audit on analyzed file"""
        vulnerabilities = []
        recommendations = []
        security_score = 100
        
        # Analyze warnings for security implications
        for warning in file_analysis.warnings:
            if any(keyword in warning.lower() for keyword in ['unsafe', 'dangerous', 'xss', 'security']):
                vulnerabilities.append(warning)
                security_score -= 10
                
        # Check file permissions (if applicable)
        try:
            file_path = Path(file_analysis.path)
            stat = file_path.stat()
            
            # Check if file is executable (potential security risk for web files)
            if stat.st_mode & 0o111:
                vulnerabilities.append("File has execute permissions")
                security_score -= 5
                recommendations.append("Remove execute permissions from web files")
                
        except Exception:
            pass
            
        # General recommendations
        if file_analysis.path.endswith('.html'):
            recommendations.extend([
                "Implement Content Security Policy (CSP) headers",
                "Validate all user inputs",
                "Use HTTPS for external resources"
            ])
        elif file_analysis.path.endswith('.js'):
            recommendations.extend([
                "Minify JavaScript in production",
                "Remove console.log statements",
                "Avoid eval() and similar dangerous functions"
            ])
            
        return SecurityCheck(
            file_path=file_analysis.path,
            vulnerabilities=vulnerabilities,
            security_score=max(0, security_score),
            recommendations=recommendations
        )
    
    def verify_emergency_panel(self) -> Dict[str, Any]:
        """Main verification method"""
        logger.info("Starting professional emergency panel verification")
        start_time = time.time()
        
        results = {
            'verification_time': None,
            'files_analyzed': [],
            'security_report': [],
            'performance_metrics': {},
            'overall_status': 'unknown',
            'recommendations': []
        }
        
        if not self.base_path.exists():
            logger.error(f"Emergency panel directory not found: {self.base_path}")
            results['overall_status'] = 'failed'
            results['errors'] = [f"Directory not found: {self.base_path}"]
            return results
            
        # Define expected files
        expected_files = {
            'index.html': 'main',
            'index_enhanced.html': 'enhanced',
            'script.js': 'main_script',
            'script-enhanced.js': 'enhanced_script', 
            'styles.css': 'styles'
        }
        
        # Analyze each file
        for filename, file_type in expected_files.items():
            file_path = self.base_path / filename
            
            if file_path.exists():
                logger.info(f"Analyzing {filename}")
                
                # Choose appropriate analyzer based on file extension
                if filename.endswith('.html'):
                    analysis = self.analyze_html_file(file_path)
                elif filename.endswith('.js'):
                    analysis = self.analyze_js_file(file_path)
                elif filename.endswith('.css'):
                    analysis = self.analyze_css_file(file_path)
                else:
                    continue
                    
                # Perform security audit
                security_check = self.security_audit(analysis)
                
                results['files_analyzed'].append({
                    'filename': filename,
                    'type': file_type,
                    'analysis': asdict(analysis),
                    'security': asdict(security_check)
                })
                
            else:
                logger.warning(f"Expected file not found: {filename}")
                results['files_analyzed'].append({
                    'filename': filename,
                    'type': file_type,
                    'status': 'missing',
                    'analysis': None,
                    'security': None
                })
        
        # Calculate overall metrics
        total_files = len(expected_files)
        found_files = len([f for f in results['files_analyzed'] if f.get('analysis')])
        
        results['performance_metrics'] = {
            'total_expected_files': total_files,
            'files_found': found_files,
            'completion_percentage': (found_files / total_files) * 100,
            'total_size_bytes': sum(
                f['analysis']['size'] for f in results['files_analyzed'] 
                if f.get('analysis')
            )
        }
        
        # Determine overall status
        if found_files == total_files:
            has_errors = any(
                f['analysis']['errors'] for f in results['files_analyzed'] 
                if f.get('analysis')
            )
            results['overall_status'] = 'failed' if has_errors else 'passed'
        else:
            results['overall_status'] = 'partial'
            
        # Generate recommendations
        all_warnings = []
        for file_info in results['files_analyzed']:
            if file_info.get('analysis'):
                all_warnings.extend(file_info['analysis']['warnings'])
                
        if all_warnings:
            results['recommendations'] = list(set(all_warnings))
            
        results['verification_time'] = time.time() - start_time
        
        logger.info(f"Verification completed in {results['verification_time']:.2f} seconds")
        logger.info(f"Overall status: {results['overall_status']}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any], output_path: str = None) -> str:
        """Generate comprehensive verification report"""
        if output_path is None:
            output_path = "/workspaces/ZeroDev_AI/reports/emergency_panel_verification.json"
            
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add metadata
        report = {
            'report_generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'verifier_version': '1.0.0',
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            **results
        }
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        logger.info(f"Verification report saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    try:
        verifier = ProfessionalEmergencyVerifier()
        results = verifier.verify_emergency_panel()
        
        # Generate report
        report_path = verifier.generate_report(results)
        
        # Print summary
        print("\n" + "="*60)
        print("🛡️  PROFESSIONAL EMERGENCY PANEL VERIFICATION REPORT")
        print("="*60)
        
        print(f"\n📊 Overall Status: {results['overall_status'].upper()}")
        print(f"⏱️  Verification Time: {results['verification_time']:.2f}s")
        
        metrics = results['performance_metrics']
        print(f"\n📈 Performance Metrics:")
        print(f"   Files Found: {metrics['files_found']}/{metrics['total_expected_files']}")
        print(f"   Completion: {metrics['completion_percentage']:.1f}%")
        print(f"   Total Size: {metrics['total_size_bytes']:,} bytes")
        
        print(f"\n📋 Files Analyzed:")
        for file_info in results['files_analyzed']:
            status = "✅" if file_info.get('analysis') else "❌"
            filename = file_info['filename']
            print(f"   {status} {filename}")
            
            if file_info.get('analysis'):
                analysis = file_info['analysis']
                if analysis['errors']:
                    print(f"      🚨 Errors: {len(analysis['errors'])}")
                if analysis['warnings']:
                    print(f"      ⚠️  Warnings: {len(analysis['warnings'])}")
                    
        if results.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(results['recommendations'][:5], 1):
                print(f"   {i}. {rec}")
                
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Exit with appropriate code
        exit_code = 0 if results['overall_status'] == 'passed' else 1
        return exit_code
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        print(f"\n❌ Verification failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
