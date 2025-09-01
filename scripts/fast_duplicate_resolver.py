#!/usr/bin/env python3
"""
Fast Duplicate Resolver - Optimized for ZeroDev AI Project

Quick detection and resolution of duplicate files with safety checks.
"""

import hashlib
import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import shutil

class FastDuplicateResolver:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.duplicates: Dict[str, List[Path]] = defaultdict(list)
        self.resolved_count = 0
        self.saved_space = 0
        
        # Directories to exclude (performance optimization)
        self.exclude_dirs = {
            '.venv', 'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'build', 'dist', '.next', 'coverage'
        }
        
        # File extensions to prioritize for duplicate checking
        self.priority_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json',
            '.md', '.yaml', '.yml', '.txt', '.sh'
        }
        
        # Safe to remove patterns
        self.safe_remove_patterns = {
            '__pycache__',
            '.pyc',
            '.pyo', 
            '.DS_Store',
            'Thumbs.db',
            '.coverage',
            'node_modules',
            '.pytest_cache'
        }

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError):
            return ""

    def should_skip_directory(self, dir_path: Path) -> bool:
        """Check if directory should be skipped"""
        return any(exclude in dir_path.parts for exclude in self.exclude_dirs)
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed for duplicates"""
        # Skip binary files that are typically large
        if file_path.suffix.lower() in {'.exe', '.so', '.dylib', '.dll', '.bin'}:
            return False
            
        # Skip very large files (>10MB) for performance
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except OSError:
            return False
            
        return True

    def find_duplicates(self) -> None:
        """Find duplicate files efficiently"""
        print("🔍 Scanning for duplicate files...")
        hash_to_files: Dict[str, List[Path]] = defaultdict(list)
        total_files = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                # Skip excluded directories
                if self.should_skip_directory(file_path):
                    continue
                    
                # Skip non-processable files
                if not self.should_process_file(file_path):
                    continue
                
                total_files += 1
                if total_files % 100 == 0:
                    print(f"   Processed {total_files} files...")
                
                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    hash_to_files[file_hash].append(file_path)
        
        # Filter out unique files (keep only duplicates)
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.duplicates[file_hash] = files
        
        print(f"✅ Found {len(self.duplicates)} sets of duplicate files")

    def display_duplicates(self) -> None:
        """Display found duplicate files in a readable format"""
        if not self.duplicates:
            print("No duplicates found.")
            return
            
        print("\n📋 Duplicate Files Found:")
        print("=" * 50)
        
        for i, (file_hash, files) in enumerate(self.duplicates.items(), 1):
            print(f"\n{i}. Duplicate Group (Hash: {file_hash[:8]}...):")
            
            # Show file size if available
            try:
                file_size = files[0].stat().st_size
                size_mb = file_size / (1024 * 1024)
                if size_mb > 1:
                    print(f"   Size: {size_mb:.2f}MB each")
                else:
                    print(f"   Size: {file_size:,} bytes each")
            except OSError:
                print("   Size: Unknown")
            
            print("   Files:")
            for file_path in files:
                # Check if file is empty (0 bytes)
                try:
                    if file_path.stat().st_size == 0:
                        print(f"   ⚠️  {file_path} (EMPTY FILE)")
                    else:
                        print(f"   📄 {file_path}")
                except OSError:
                    print(f"   ❌ {file_path} (NOT ACCESSIBLE)")
            
            if i >= 10:  # Limit display to first 10 groups
                remaining = len(self.duplicates) - 10
                print(f"\n... and {remaining} more duplicate groups")
                break

    def analyze_duplicates(self) -> Dict:
        """Analyze duplicate files and categorize them"""
        analysis = {
            'total_duplicate_sets': len(self.duplicates),
            'total_duplicate_files': 0,
            'potential_space_savings': 0,
            'safe_to_remove': [],
            'manual_review_needed': [],
            'by_extension': defaultdict(int),
            'by_directory': defaultdict(int)
        }
        
        for file_hash, files in self.duplicates.items():
            duplicate_count = len(files) - 1  # Keep one original
            analysis['total_duplicate_files'] += duplicate_count
            
            # Calculate space savings
            try:
                file_size = files[0].stat().st_size
                analysis['potential_space_savings'] += file_size * duplicate_count
            except OSError:
                continue
            
            # Categorize by extension
            ext = files[0].suffix.lower()
            analysis['by_extension'][ext] += duplicate_count
            
            # Categorize by directory
            for file_path in files:
                analysis['by_directory'][str(file_path.parent)] += 1
            
            # Determine if safe to auto-remove
            if self._is_safe_to_auto_remove(files):
                analysis['safe_to_remove'].append({
                    'hash': file_hash,
                    'files': [str(f) for f in files],
                    'keep': str(files[0]),  # Keep first one
                    'remove': [str(f) for f in files[1:]]
                })
            else:
                analysis['manual_review_needed'].append({
                    'hash': file_hash,
                    'files': [str(f) for f in files],
                    'reason': self._get_manual_review_reason(files)
                })
        
        return analysis

    def _is_safe_to_auto_remove(self, files: List[Path]) -> bool:
        """Determine if duplicates are safe to auto-remove"""
        # Check if all files are in safe patterns
        for file_path in files:
            if any(pattern in str(file_path) for pattern in self.safe_remove_patterns):
                continue
            
            # If files are in different important directories, manual review needed
            important_dirs = {'src', 'backend', 'frontend', 'api', 'components'}
            if any(important in file_path.parts for important in important_dirs):
                # Check if other duplicates are also in important dirs
                other_important = [f for f in files if f != file_path and 
                                 any(imp in f.parts for imp in important_dirs)]
                if other_important:
                    return False
        
        return True

    def _get_manual_review_reason(self, files: List[Path]) -> str:
        """Get reason why manual review is needed"""
        reasons = []
        
        # Check for important directories
        important_dirs = {'src', 'backend', 'frontend', 'api', 'components'}
        important_files = [f for f in files if any(imp in f.parts for imp in important_dirs)]
        
        if len(important_files) > 1:
            reasons.append("Multiple files in important directories")
        
        # Check for different extensions
        extensions = {f.suffix for f in files}
        if len(extensions) > 1:
            reasons.append("Different file extensions")
        
        # Check for core files
        core_names = {'__init__.py', 'index.js', 'main.py', 'app.py'}
        if any(f.name in core_names for f in files):
            reasons.append("Core application files")
            
        return "; ".join(reasons) if reasons else "Requires manual verification"

    def auto_resolve_safe_duplicates(self, analysis: Dict) -> None:
        """Automatically resolve safe duplicate files"""
        print("\n🔧 Auto-resolving safe duplicates...")
        
        for item in analysis['safe_to_remove']:
            try:
                keep_file = Path(item['keep'])
                
                for remove_file_str in item['remove']:
                    remove_file = Path(remove_file_str)
                    
                    if remove_file.exists():
                        file_size = remove_file.stat().st_size
                        remove_file.unlink()
                        
                        self.resolved_count += 1
                        self.saved_space += file_size
                        
                        print(f"   ✅ Removed: {remove_file.relative_to(self.project_root)}")
                        
            except Exception as e:
                print(f"   ❌ Error removing {remove_file_str}: {e}")

    def generate_report(self, analysis: Dict) -> None:
        """Generate comprehensive duplicate analysis report"""
        report = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'analysis': analysis,
            'resolved': {
                'auto_resolved_count': self.resolved_count,
                'space_saved_bytes': self.saved_space,
                'space_saved_mb': round(self.saved_space / (1024 * 1024), 2)
            }
        }
        
        report_file = self.project_root / 'DUPLICATE_ANALYSIS_REPORT.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved to: {report_file}")

    def resolve_duplicates(self) -> None:
        """Main method to resolve duplicates"""
        print("=" * 60)
        print("🚀 FAST DUPLICATE RESOLVER")
        print("=" * 60)
        
        # Step 1: Find duplicates
        self.find_duplicates()
        
        if not self.duplicates:
            print("✅ No duplicate files found!")
            return
        
        # Step 2: Analyze duplicates
        print("\n📊 Analyzing duplicates...")
        analysis = self.analyze_duplicates()
        
        # Step 3: Display summary
        print(f"\n📈 DUPLICATE ANALYSIS SUMMARY:")
        print(f"   Total duplicate sets: {analysis['total_duplicate_sets']}")
        print(f"   Total duplicate files: {analysis['total_duplicate_files']}")
        print(f"   Potential space savings: {analysis['potential_space_savings'] / (1024*1024):.2f} MB")
        print(f"   Safe to auto-remove: {len(analysis['safe_to_remove'])}")
        print(f"   Need manual review: {len(analysis['manual_review_needed'])}")
        
        # Step 4: Auto-resolve safe duplicates
        if analysis['safe_to_remove']:
            self.auto_resolve_safe_duplicates(analysis)
            
            print(f"\n✅ AUTO-RESOLUTION COMPLETE:")
            print(f"   Files removed: {self.resolved_count}")
            print(f"   Space saved: {self.saved_space / (1024*1024):.2f} MB")
        
        # Step 5: Generate report
        self.generate_report(analysis)
        
        # Step 6: Display manual review needed
        if analysis['manual_review_needed']:
            print(f"\n⚠️  MANUAL REVIEW NEEDED ({len(analysis['manual_review_needed'])} items):")
            for i, item in enumerate(analysis['manual_review_needed'][:5], 1):  # Show first 5
                print(f"   {i}. {item['reason']}:")
                for file_path in item['files']:
                    print(f"      - {file_path}")
                print()
            
            if len(analysis['manual_review_needed']) > 5:
                print(f"   ... and {len(analysis['manual_review_needed']) - 5} more items")
                print("   📄 See full report for details")


def main():
    project_root = "/workspaces/ZeroDev_AI"
    
    if not Path(project_root).exists():
        print(f"❌ Project root not found: {project_root}")
        return
    
    resolver = FastDuplicateResolver(project_root)
    
    print("🔍 Fast Duplicate Scan Starting (SAFETY MODE)...")
    resolver.find_duplicates()
    
    if resolver.duplicates:
        print(f"\n📊 Found {len(resolver.duplicates)} duplicate groups")
        resolver.display_duplicates()
        
        # SAFETY MODE: Only scan, don't resolve automatically
        print("\n⚠️ SAFETY MODE: Duplicates found but not resolved automatically")
        print("Review the duplicates above manually before resolving.")
    else:
        print("✅ No duplicates found!")


if __name__ == "__main__":
    main()
