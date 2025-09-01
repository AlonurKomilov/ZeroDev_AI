#!/usr/bin/env python3
"""
ZeroDev AI Project Structure Analyzer
=====================================

Bu script loyihadagi barcha muammolarni aniqlaydi:
- Duplicate kodlar
- Cache muammolari  
- Noto'g'ri arxitektura
- Import cycles
- Dead code
- File naming inconsistencies
"""

import os
import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter
import re

class ProjectAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = {
            'duplicates': [],
            'cache_issues': [],
            'architecture_violations': [],
            'naming_issues': [],
            'import_cycles': [],
            'dead_code': [],
            'config_conflicts': []
        }
    
    def analyze(self) -> Dict[str, Any]:
        """Loyihani to'liq tahlil qilish"""
        print("🔍 ZeroDev AI Project Analysis boshlandi...")
        
        self._find_duplicate_files()
        self._find_duplicate_code()
        self._analyze_cache_issues()
        self._check_architecture_violations()
        self._check_naming_conventions()
        self._detect_import_cycles()
        self._find_dead_code()
        self._check_config_conflicts()
        
        return self._generate_report()
    
    def _find_duplicate_files(self):
        """Bir xil content'ga ega file'larni topish"""
        print("📄 Duplicate file'larni qidirayapman...")
        
        file_hashes = defaultdict(list)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        file_hash = hashlib.md5(content).hexdigest()
                        file_hashes[file_hash].append(str(file_path))
                except:
                    continue
        
        # Duplicate'larni topish
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.issues['duplicates'].append({
                    'type': 'identical_files',
                    'files': files,
                    'hash': file_hash
                })
    
    def _find_duplicate_code(self):
        """Code duplicate'larini topish"""
        print("💾 Code duplicate'larni qidirayapman...")
        
        python_files = list(self.project_root.rglob("*.py"))
        code_blocks = defaultdict(list)
        
        for py_file in python_files:
            if self._should_ignore_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Function'larni extract qilish
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        code_snippet = ast.get_source_segment(content, node)
                        if code_snippet and len(code_snippet) > 100:  # Kichik function'larni ignore
                            code_hash = hashlib.md5(code_snippet.encode()).hexdigest()
                            code_blocks[code_hash].append({
                                'file': str(py_file),
                                'name': node.name,
                                'type': type(node).__name__,
                                'line': node.lineno
                            })
            except:
                continue
        
        # Duplicate code'larni topish
        for code_hash, occurrences in code_blocks.items():
            if len(occurrences) > 1:
                self.issues['duplicates'].append({
                    'type': 'duplicate_code',
                    'occurrences': occurrences,
                    'hash': code_hash
                })
    
    def _analyze_cache_issues(self):
        """Cache muammolarini aniqlash"""
        print("🗂️  Cache muammolarini tekshirayapman...")
        
        cache_dirs = [
            '__pycache__',
            '.pytest_cache', 
            'node_modules',
            '.next',
            'dist',
            'build',
            '.cache'
        ]
        
        for cache_dir in cache_dirs:
            found_dirs = list(self.project_root.rglob(cache_dir))
            for dir_path in found_dirs:
                if dir_path.is_dir():
                    size = self._get_directory_size(dir_path)
                    self.issues['cache_issues'].append({
                        'type': 'cache_directory',
                        'path': str(dir_path),
                        'size_mb': round(size / 1024 / 1024, 2)
                    })
        
        # Large files (potential cache issues)
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size > 1024 * 1024:  # 1MB dan katta
                self.issues['cache_issues'].append({
                    'type': 'large_file',
                    'path': str(file_path),
                    'size_mb': round(file_path.stat().st_size / 1024 / 1024, 2)
                })
    
    def _check_architecture_violations(self):
        """Arxitektura violations'ni tekshirish"""
        print("🏗️  Arxitektura violations'ni tekshirayapman...")
        
        # Backend structure check
        backend_path = self.project_root / "backend"
        if backend_path.exists():
            expected_dirs = ['api', 'core', 'models', 'services', 'tests']
            for expected in expected_dirs:
                if not (backend_path / expected).exists():
                    self.issues['architecture_violations'].append({
                        'type': 'missing_directory',
                        'expected': str(backend_path / expected)
                    })
        
        # Import violations (backend files importing frontend)
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if 'backend' in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'from frontend' in content or 'import frontend' in content:
                            self.issues['architecture_violations'].append({
                                'type': 'cross_boundary_import',
                                'file': str(py_file),
                                'violation': 'Backend importing from frontend'
                            })
                except:
                    continue
    
    def _check_naming_conventions(self):
        """Naming convention'larni tekshirish"""
        print("📝 Naming convention'larni tekshirayapman...")
        
        # Python files should be snake_case
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            filename = py_file.stem
            if not re.match(r'^[a-z][a-z0-9_]*$', filename) and filename != '__init__':
                self.issues['naming_issues'].append({
                    'type': 'python_naming',
                    'file': str(py_file),
                    'issue': f'File name "{filename}" is not snake_case'
                })
        
        # TypeScript/JavaScript files should be camelCase or kebab-case
        js_files = list(self.project_root.rglob("*.tsx")) + list(self.project_root.rglob("*.ts")) + list(self.project_root.rglob("*.js"))
        for js_file in js_files:
            filename = js_file.stem
            if not re.match(r'^[a-z][a-zA-Z0-9]*$|^[a-z][a-z0-9-]*$', filename):
                self.issues['naming_issues'].append({
                    'type': 'js_naming', 
                    'file': str(js_file),
                    'issue': f'File name "{filename}" is not camelCase or kebab-case'
                })
    
    def _detect_import_cycles(self):
        """Import cycle'larni aniqlash"""
        print("🔄 Import cycle'larni qidirayapman...")
        
        import_graph = defaultdict(set)
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                import_graph[str(py_file)].add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                import_graph[str(py_file)].add(node.module)
            except:
                continue
        
        # Simple cycle detection (bu real implementation emas, basic check)
        # Real cycle detection uchun graph algorithms kerak
    
    def _find_dead_code(self):
        """O'lik kod topish"""
        print("💀 Dead code'ni qidirayapman...")
        
        # Unused imports
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Basic unused import detection
                import_lines = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                        import_lines.append((line_num, line.strip()))
                
                # Bu basic check, real implementation uchun AST analysis kerak
                
            except:
                continue
    
    def _check_config_conflicts(self):
        """Config file'lardagi conflicts"""
        print("⚙️  Config conflicts'ni tekshirayapman...")
        
        config_files = [
            'package.json',
            'pyproject.toml', 
            'requirements.txt',
            'tsconfig.json',
            'next.config.mjs'
        ]
        
        found_configs = {}
        for config_file in config_files:
            configs = list(self.project_root.rglob(config_file))
            if len(configs) > 1:
                found_configs[config_file] = [str(c) for c in configs]
        
        if found_configs:
            self.issues['config_conflicts'].extend([
                {
                    'type': 'multiple_configs',
                    'config_type': config_type,
                    'files': files
                }
                for config_type, files in found_configs.items()
            ])
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Ignore qilinadigan file'larni aniqlash"""
        ignore_patterns = [
            '__pycache__',
            '.git',
            '.next',
            'node_modules',
            '.pytest_cache',
            'dist',
            'build',
            '.vscode',
            '.idea',
            '*.pyc',
            '*.log'
        ]
        
        str_path = str(file_path)
        return any(pattern in str_path for pattern in ignore_patterns)
    
    def _get_directory_size(self, directory: Path) -> int:
        """Directory hajmini hisoblash"""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except:
                    continue
        return total_size
    
    def _generate_report(self) -> Dict[str, Any]:
        """Final reportni yaratish"""
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        report = {
            'summary': {
                'total_issues': total_issues,
                'duplicates': len(self.issues['duplicates']),
                'cache_issues': len(self.issues['cache_issues']),
                'architecture_violations': len(self.issues['architecture_violations']),
                'naming_issues': len(self.issues['naming_issues']),
                'import_cycles': len(self.issues['import_cycles']),
                'dead_code': len(self.issues['dead_code']),
                'config_conflicts': len(self.issues['config_conflicts'])
            },
            'details': self.issues,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Tavsiyalar berish"""
        recommendations = []
        
        if self.issues['duplicates']:
            recommendations.append("🔄 Duplicate file'lar va kod'larni birlashtirishingiz kerak")
        
        if self.issues['cache_issues']:
            recommendations.append("🗑️  Cache directory'larni tozalashingiz kerak")
        
        if self.issues['architecture_violations']:
            recommendations.append("🏗️  Arxitektura violations'ni to'g'rilashingiz kerak")
        
        if self.issues['naming_issues']:
            recommendations.append("📝 File naming convention'larni to'g'rilashingiz kerak")
        
        return recommendations

def main():
    """Main function"""
    project_root = "/workspaces/ZeroDev_AI"
    analyzer = ProjectAnalyzer(project_root)
    
    print("=" * 60)
    print("🚀 ZeroDev AI PROJECT STRUCTURE ANALYSIS")
    print("=" * 60)
    
    report = analyzer.analyze()
    
    # Report'ni file'ga saqlash
    with open(f"{project_root}/PROJECT_ANALYSIS_REPORT.json", 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Summary print qilish
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    summary = report['summary']
    print(f"💥 Jami muammolar: {summary['total_issues']}")
    print(f"🔄 Duplicates: {summary['duplicates']}")
    print(f"🗂️  Cache issues: {summary['cache_issues']}")  
    print(f"🏗️  Architecture violations: {summary['architecture_violations']}")
    print(f"📝 Naming issues: {summary['naming_issues']}")
    print(f"🔄 Import cycles: {summary['import_cycles']}")
    print(f"💀 Dead code: {summary['dead_code']}")
    print(f"⚙️  Config conflicts: {summary['config_conflicts']}")
    
    print("\n📋 TAVSIYALAR:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    print(f"\n📄 Batafsil report: PROJECT_ANALYSIS_REPORT.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
