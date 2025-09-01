#!/usr/bin/env python3
"""
Professional Duplicate Files & Similar Code Cleaner
Advanced duplicate detection and intelligent file cleanup
"""

import os
import re
import json
import hashlib
import logging
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/ZeroDev_AI/logs/duplicate_cleaner.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Information about a file"""
    path: str
    size: int
    hash_md5: str
    hash_sha256: str
    modified_time: float
    content_hash: str  # Content-specific hash for code files
    file_type: str
    lines_count: int
    
@dataclass
class DuplicateGroup:
    """Group of duplicate files"""
    hash_key: str
    files: List[FileInfo]
    duplicate_type: str  # 'exact', 'content', 'similar'
    similarity_score: float
    recommended_action: str
    
@dataclass
class SimilarityMatch:
    """Files with similar content"""
    file1: str
    file2: str
    similarity: float
    common_lines: int
    differences: List[str]

class ProfessionalDuplicateCleaner:
    """Professional duplicate files and similar code cleaner"""
    
    def __init__(self, project_path: str = "/workspaces/ZeroDev_AI"):
        self.project_path = Path(project_path)
        self.file_types = {
            'code': ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.env'],
            'docs': ['.md', '.txt', '.rst'],
            'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'],
            'other': []
        }
        
        self.ignore_patterns = [
            r'__pycache__',
            r'\.git',
            r'node_modules',
            r'\.next',
            r'dist',
            r'build',
            r'\.pytest_cache',
            r'\.vscode',
            r'\.idea'
        ]
        
        # Ensure logs directory exists
        os.makedirs("/workspaces/ZeroDev_AI/logs", exist_ok=True)
    
    def should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        path_str = str(file_path)
        return any(re.search(pattern, path_str) for pattern in self.ignore_patterns)
    
    def get_file_type(self, file_path: Path) -> str:
        """Determine file type based on extension"""
        suffix = file_path.suffix.lower()
        
        for file_type, extensions in self.file_types.items():
            if suffix in extensions:
                return file_type
        return 'other'
    
    def calculate_content_hash(self, file_path: Path, file_type: str) -> str:
        """Calculate content-specific hash for intelligent comparison"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if file_type == 'code':
                # Normalize code content for better duplicate detection
                normalized = self.normalize_code_content(content)
                return hashlib.md5(normalized.encode()).hexdigest()
            else:
                # For non-code files, use content as-is
                return hashlib.md5(content.encode()).hexdigest()
                
        except Exception as e:
            logger.debug(f"Failed to calculate content hash for {file_path}: {e}")
            return ""
    
    def normalize_code_content(self, content: str) -> str:
        """Normalize code content for better duplicate detection"""
        lines = content.splitlines()
        normalized_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines and comments (basic detection)
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # Remove extra whitespace within line
            line = ' '.join(line.split())
            
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def scan_files(self) -> List[FileInfo]:
        """Scan all files in the project"""
        logger.info(f"Scanning files in {self.project_path}")
        files_info = []
        
        try:
            for file_path in self.project_path.rglob('*'):
                if not file_path.is_file() or self.should_ignore(file_path):
                    continue
                
                try:
                    stat = file_path.stat()
                    file_type = self.get_file_type(file_path)
                    
                    # Calculate hashes
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    md5_hash = hashlib.md5(content).hexdigest()
                    sha256_hash = hashlib.sha256(content).hexdigest()
                    
                    # Count lines for text files
                    lines_count = 0
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines_count = sum(1 for _ in f)
                    except:
                        lines_count = 0
                    
                    # Calculate content hash
                    content_hash = self.calculate_content_hash(file_path, file_type)
                    
                    file_info = FileInfo(
                        path=str(file_path.relative_to(self.project_path)),
                        size=stat.st_size,
                        hash_md5=md5_hash,
                        hash_sha256=sha256_hash,
                        modified_time=stat.st_mtime,
                        content_hash=content_hash,
                        file_type=file_type,
                        lines_count=lines_count
                    )
                    
                    files_info.append(file_info)
                    
                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scanning files: {e}")
        
        logger.info(f"Scanned {len(files_info)} files")
        return files_info
    
    def find_exact_duplicates(self, files_info: List[FileInfo]) -> List[DuplicateGroup]:
        """Find files with identical content"""
        logger.info("Finding exact duplicates...")
        
        # Group by SHA256 hash (most reliable for exact duplicates)
        hash_groups = defaultdict(list)
        
        for file_info in files_info:
            if file_info.size > 0:  # Skip empty files
                hash_groups[file_info.hash_sha256].append(file_info)
        
        # Find groups with multiple files
        duplicate_groups = []
        for hash_key, files in hash_groups.items():
            if len(files) > 1:
                # Sort by modification time (newest first)
                files.sort(key=lambda f: f.modified_time, reverse=True)
                
                # Recommend keeping the newest file
                recommended_action = f"Keep '{files[0].path}', remove others"
                
                group = DuplicateGroup(
                    hash_key=hash_key,
                    files=files,
                    duplicate_type='exact',
                    similarity_score=1.0,
                    recommended_action=recommended_action
                )
                duplicate_groups.append(group)
        
        logger.info(f"Found {len(duplicate_groups)} exact duplicate groups")
        return duplicate_groups
    
    def find_content_duplicates(self, files_info: List[FileInfo]) -> List[DuplicateGroup]:
        """Find files with identical content (ignoring whitespace for code)"""
        logger.info("Finding content duplicates...")
        
        # Group by content hash
        content_groups = defaultdict(list)
        
        for file_info in files_info:
            if file_info.content_hash and file_info.file_type == 'code':
                content_groups[file_info.content_hash].append(file_info)
        
        duplicate_groups = []
        for hash_key, files in content_groups.items():
            if len(files) > 1:
                # Sort by path length (prefer shorter, more generic paths)
                files.sort(key=lambda f: len(f.path))
                
                recommended_action = f"Keep '{files[0].path}', review others"
                
                group = DuplicateGroup(
                    hash_key=hash_key,
                    files=files,
                    duplicate_type='content',
                    similarity_score=0.95,
                    recommended_action=recommended_action
                )
                duplicate_groups.append(group)
        
        logger.info(f"Found {len(duplicate_groups)} content duplicate groups")
        return duplicate_groups
    
    def find_similar_files(self, files_info: List[FileInfo], 
                          similarity_threshold: float = 0.8) -> List[SimilarityMatch]:
        """Find files with similar content"""
        logger.info("Finding similar files...")
        
        # Only compare code files
        code_files = [f for f in files_info if f.file_type == 'code' and f.lines_count > 10]
        
        similarities = []
        
        for i, file1 in enumerate(code_files):
            for file2 in code_files[i+1:]:
                try:
                    # Read file contents
                    path1 = self.project_path / file1.path
                    path2 = self.project_path / file2.path
                    
                    with open(path1, 'r', encoding='utf-8', errors='ignore') as f:
                        content1 = f.read().splitlines()
                    
                    with open(path2, 'r', encoding='utf-8', errors='ignore') as f:
                        content2 = f.read().splitlines()
                    
                    # Calculate similarity
                    matcher = difflib.SequenceMatcher(None, content1, content2)
                    similarity = matcher.ratio()
                    
                    if similarity >= similarity_threshold:
                        # Get common lines
                        common_lines = sum(1 for block in matcher.get_matching_blocks() 
                                         if block.size > 0)
                        
                        # Get differences
                        differences = list(difflib.unified_diff(
                            content1[:5], content2[:5], 
                            fromfile=file1.path, tofile=file2.path, n=0
                        ))
                        
                        match = SimilarityMatch(
                            file1=file1.path,
                            file2=file2.path,
                            similarity=similarity,
                            common_lines=common_lines,
                            differences=differences[:10]  # Limit differences
                        )
                        similarities.append(match)
                        
                except Exception as e:
                    logger.debug(f"Error comparing {file1.path} and {file2.path}: {e}")
                    continue
        
        logger.info(f"Found {len(similarities)} similar file pairs")
        return similarities
    
    def analyze_duplicates(self, files_info: List[FileInfo]) -> Dict[str, Any]:
        """Complete duplicate analysis"""
        logger.info("Starting comprehensive duplicate analysis...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(files_info),
            'total_size': sum(f.size for f in files_info),
            'file_types': {},
            'exact_duplicates': [],
            'content_duplicates': [],
            'similar_files': [],
            'recommendations': []
        }
        
        # Analyze file types
        type_counts = defaultdict(int)
        type_sizes = defaultdict(int)
        
        for file_info in files_info:
            type_counts[file_info.file_type] += 1
            type_sizes[file_info.file_type] += file_info.size
        
        results['file_types'] = {
            ftype: {'count': type_counts[ftype], 'size': type_sizes[ftype]}
            for ftype in type_counts
        }
        
        # Find duplicates
        exact_duplicates = self.find_exact_duplicates(files_info)
        content_duplicates = self.find_content_duplicates(files_info)
        similar_files = self.find_similar_files(files_info)
        
        results['exact_duplicates'] = [asdict(group) for group in exact_duplicates]
        results['content_duplicates'] = [asdict(group) for group in content_duplicates]
        results['similar_files'] = [asdict(match) for match in similar_files]
        
        # Calculate potential savings
        exact_savings = sum(
            sum(f.size for f in group.files[1:])  # All files except the first (kept)
            for group in exact_duplicates
        )
        
        content_savings = sum(
            sum(f.size for f in group.files[1:])
            for group in content_duplicates
        )
        
        results['potential_savings'] = {
            'exact_duplicates_bytes': exact_savings,
            'content_duplicates_bytes': content_savings,
            'total_bytes': exact_savings + content_savings
        }
        
        # Generate recommendations
        recommendations = []
        
        if exact_duplicates:
            recommendations.append(f"Found {len(exact_duplicates)} groups of exact duplicates - safe to remove")
        
        if content_duplicates:
            recommendations.append(f"Found {len(content_duplicates)} groups of content duplicates - review before removing")
        
        if similar_files:
            recommendations.append(f"Found {len(similar_files)} pairs of similar files - consider refactoring")
        
        if exact_savings > 1024 * 1024:  # 1MB
            recommendations.append(f"Can save {exact_savings / (1024*1024):.1f}MB by removing exact duplicates")
        
        results['recommendations'] = recommendations
        
        return results
    
    def clean_duplicates(self, duplicate_groups: List[DuplicateGroup], 
                        dry_run: bool = True) -> Dict[str, List[str]]:
        """Clean up duplicate files"""
        results = {
            'removed': [],
            'kept': [],
            'errors': []
        }
        
        for group in duplicate_groups:
            # Keep the first file (recommended), remove others
            keep_file = group.files[0]
            results['kept'].append(keep_file.path)
            
            for file_to_remove in group.files[1:]:
                file_path = self.project_path / file_to_remove.path
                
                try:
                    if not dry_run:
                        file_path.unlink()
                        logger.info(f"Removed duplicate: {file_to_remove.path}")
                    else:
                        logger.info(f"Would remove: {file_to_remove.path}")
                    
                    results['removed'].append(file_to_remove.path)
                    
                except Exception as e:
                    error_msg = f"Failed to remove {file_to_remove.path}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
        
        return results
    
    def save_report(self, analysis_results: Dict[str, Any], output_path: str = None) -> str:
        """Save analysis report"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/workspaces/ZeroDev_AI/reports/duplicate_analysis_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        logger.info(f"Analysis report saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Professional Duplicate Files Cleaner")
    parser.add_argument("--path", type=str, default="/workspaces/ZeroDev_AI",
                       help="Project path to analyze")
    parser.add_argument("--clean", action="store_true", help="Actually remove duplicates")
    parser.add_argument("--similarity", type=float, default=0.8,
                       help="Similarity threshold for finding similar files")
    parser.add_argument("--output", type=str, help="Output report path")
    
    args = parser.parse_args()
    
    try:
        cleaner = ProfessionalDuplicateCleaner(args.path)
        
        # Scan files
        print("🔍 Scanning project files...")
        files_info = cleaner.scan_files()
        
        # Analyze duplicates
        print("📊 Analyzing duplicates...")
        results = cleaner.analyze_duplicates(files_info)
        
        # Clean duplicates if requested
        cleanup_results = {}
        if args.clean:
            print("🧹 Cleaning exact duplicates...")
            exact_duplicates = [DuplicateGroup(**group) for group in results['exact_duplicates']]
            cleanup_results = cleaner.clean_duplicates(exact_duplicates, dry_run=False)
            results['cleanup_results'] = cleanup_results
        
        # Save report
        report_path = cleaner.save_report(results, args.output)
        
        # Print summary
        print("\n" + "="*70)
        print("🗂️  DUPLICATE FILES ANALYSIS REPORT")
        print("="*70)
        
        print(f"\n📊 Project Summary:")
        print(f"   📁 Total Files: {results['total_files']:,}")
        print(f"   💾 Total Size: {results['total_size'] / (1024*1024):.1f} MB")
        
        print(f"\n🔍 Duplicates Found:")
        print(f"   🎯 Exact Duplicates: {len(results['exact_duplicates'])} groups")
        print(f"   📝 Content Duplicates: {len(results['content_duplicates'])} groups") 
        print(f"   🔗 Similar Files: {len(results['similar_files'])} pairs")
        
        savings = results['potential_savings']
        total_savings = savings['total_bytes']
        if total_savings > 0:
            print(f"\n💰 Potential Savings:")
            print(f"   💾 Space: {total_savings / (1024*1024):.1f} MB")
        
        if cleanup_results:
            print(f"\n🧹 Cleanup Results:")
            print(f"   ✅ Removed: {len(cleanup_results['removed'])} files")
            print(f"   🛡️  Kept: {len(cleanup_results['kept'])} files")
            if cleanup_results['errors']:
                print(f"   ❌ Errors: {len(cleanup_results['errors'])}")
        
        if results['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📄 Detailed report: {report_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Duplicate analysis failed: {e}")
        print(f"\n❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
