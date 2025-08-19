#!/usr/bin/env python3
"""
ZeroDev AI Duplicate Resolver
============================

Bu script duplicate files va code'larni aniqlaydi va hal qiladi:
- Exact file duplicates
- Similar code blocks
- Redundant implementations
"""

import os
import json
import hashlib
import difflib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class DuplicateResolver:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.duplicates = {
            'exact_files': [],
            'similar_files': [],
            'code_blocks': []
        }
        self.resolved = []
        self.skipped = []
    
    def resolve_duplicates(self):
        """Duplicate'larni aniqlash va hal qilish"""
        print("🔍 Duplicate files'ni qidiraman...")
        
        # Exact file duplicates
        self._find_exact_duplicates()
        
        # Similar content files
        self._find_similar_files()
        
        # Code block duplicates
        self._find_duplicate_code_blocks()
        
        # Duplicate'larni resolve qilish
        self._resolve_exact_duplicates()
        
        self._generate_report()
    
    def _find_exact_duplicates(self):
        """Aynan bir xil file'larni topish"""
        print("📋 Exact duplicate files'ni qidiraman...")
        
        file_hashes = defaultdict(list)
        
        # Barcha file'larni hash qilish
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and self._should_process_file(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hashes[file_hash].append(file_path)
                except Exception as e:
                    continue
        
        # Duplicate'larni saqlash
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.duplicates['exact_files'].append({
                    'hash': file_hash,
                    'files': [str(f) for f in files],
                    'size': files[0].stat().st_size if files[0].exists() else 0
                })
                print(f"  🔴 Found {len(files)} exact duplicates: {files[0].name}")
    
    def _find_similar_files(self):
        """O'xshash content'li file'larni topish"""
        print("📊 Similar content files'ni qidiraman...")
        
        text_files = []
        
        # Text file'larni yig'ish
        for file_path in self.project_root.rglob("*"):
            if (file_path.is_file() and 
                self._should_process_file(file_path) and
                self._is_text_file(file_path)):
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content) > 100:  # Minimum content
                            text_files.append((file_path, content))
                except Exception:
                    continue
        
        # Similarity check
        for i, (file1, content1) in enumerate(text_files):
            for j, (file2, content2) in enumerate(text_files[i+1:], i+1):
                similarity = self._calculate_similarity(content1, content2)
                
                if similarity > 0.8:  # 80% similar
                    self.duplicates['similar_files'].append({
                        'file1': str(file1),
                        'file2': str(file2),
                        'similarity': similarity,
                        'size1': len(content1),
                        'size2': len(content2)
                    })
                    print(f"  🟡 Similar files ({similarity:.1%}): {file1.name} ↔ {file2.name}")
    
    def _find_duplicate_code_blocks(self):
        """Duplicate code block'larni topish"""
        print("🧩 Duplicate code blocks qidiraman...")
        
        code_files = []
        
        # Code file'larni yig'ish  
        for file_path in self.project_root.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix in ['.py', '.js', '.ts', '.tsx'] and
                self._should_process_file(file_path)):
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        code_files.append((file_path, lines))
                except Exception:
                    continue
        
        # Block duplicate'larni qidirish
        for file1, lines1 in code_files:
            for file2, lines2 in code_files:
                if file1 >= file2:  # Avoid duplicates
                    continue
                    
                duplicates = self._find_duplicate_blocks(lines1, lines2)
                
                if duplicates:
                    self.duplicates['code_blocks'].append({
                        'file1': str(file1),
                        'file2': str(file2),
                        'blocks': duplicates
                    })
    
    def _resolve_exact_duplicates(self):
        """Exact duplicate'larni hal qilish"""
        print("🔧 Exact duplicate'larni hal qilaman...")
        
        for dup_group in self.duplicates['exact_files']:
            files = [Path(f) for f in dup_group['files']]
            
            # Eng yaxshi file'ni tanlash (path bo'yicha)
            primary_file = min(files, key=lambda f: (len(f.parts), str(f)))
            duplicate_files = [f for f in files if f != primary_file]
            
            print(f"  📌 Primary: {primary_file}")
            
            # Duplicate'larni o'chirish
            for dup_file in duplicate_files:
                try:
                    if dup_file.exists():
                        dup_file.unlink()
                        self.resolved.append({
                            'action': 'deleted_duplicate',
                            'file': str(dup_file),
                            'primary': str(primary_file),
                            'size_saved': dup_group['size']
                        })
                        print(f"    ✅ Deleted: {dup_file}")
                except Exception as e:
                    self.skipped.append({
                        'file': str(dup_file),
                        'reason': str(e)
                    })
                    print(f"    ❌ Failed to delete: {dup_file}")
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Matn similarity'ni hisoblash"""
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def _find_duplicate_blocks(self, lines1: List[str], lines2: List[str], min_lines: int = 5) -> List[Dict]:
        """Code block duplicate'larni topish"""
        duplicates = []
        
        for i in range(len(lines1) - min_lines):
            for j in range(len(lines2) - min_lines):
                # Block'ni taqqoslash
                block1 = lines1[i:i+min_lines]
                block2 = lines2[j:j+min_lines]
                
                # Clean comparison (whitespace ignore)
                clean1 = [line.strip() for line in block1 if line.strip()]
                clean2 = [line.strip() for line in block2 if line.strip()]
                
                if len(clean1) >= 3 and clean1 == clean2:
                    duplicates.append({
                        'start1': i + 1,
                        'end1': i + min_lines,
                        'start2': j + 1, 
                        'end2': j + min_lines,
                        'lines': min_lines
                    })
        
        return duplicates
    
    def _should_process_file(self, file_path: Path) -> bool:
        """File process qilinishi kerakmi?"""
        skip_patterns = [
            '.vscode', 'node_modules', '.git', '__pycache__',
            '.next', 'dist', 'build', '.pytest_cache',
            'bun.lock', 'package-lock.json'
        ]
        
        str_path = str(file_path)
        return not any(pattern in str_path for pattern in skip_patterns)
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Text file ekanmi?"""
        text_extensions = {
            '.py', '.js', '.ts', '.tsx', '.json', '.md', 
            '.txt', '.yml', '.yaml', '.toml', '.ini', '.cfg',
            '.html', '.css', '.scss', '.sql'
        }
        return file_path.suffix.lower() in text_extensions
    
    def _generate_report(self):
        """Report yaratish"""
        print("\n" + "=" * 60)
        print("🔍 DUPLICATE RESOLUTION SUMMARY")
        print("=" * 60)
        
        # Statistics
        total_exact = len(self.duplicates['exact_files'])
        total_similar = len(self.duplicates['similar_files'])
        total_code_blocks = len(self.duplicates['code_blocks'])
        total_resolved = len(self.resolved)
        
        # Space saved
        space_saved = sum(r.get('size_saved', 0) for r in self.resolved)
        
        print(f"📋 Exact file duplicates: {total_exact}")
        print(f"📊 Similar files: {total_similar}")
        print(f"🧩 Code block duplicates: {total_code_blocks}")
        print(f"✅ Resolved: {total_resolved}")
        print(f"💾 Space saved: {space_saved / 1024 / 1024:.2f} MB")
        
        # Similar files detail
        if self.duplicates['similar_files']:
            print("\n🔍 SIMILAR FILES FOUND:")
            for sim in self.duplicates['similar_files'][:10]:  # Top 10
                print(f"  {sim['similarity']:.1%} similar:")
                print(f"    {Path(sim['file1']).name}")
                print(f"    {Path(sim['file2']).name}")
        
        # Code blocks detail
        if self.duplicates['code_blocks']:
            print("\n🧩 DUPLICATE CODE BLOCKS:")
            for block in self.duplicates['code_blocks'][:5]:  # Top 5
                print(f"  {Path(block['file1']).name} ↔ {Path(block['file2']).name}")
                print(f"    {len(block['blocks'])} duplicate blocks found")
        
        # Report'ni saqlash
        report = {
            'duplicates_found': self.duplicates,
            'resolved_items': self.resolved,
            'skipped_items': self.skipped,
            'statistics': {
                'exact_duplicates': total_exact,
                'similar_files': total_similar, 
                'code_blocks': total_code_blocks,
                'resolved': total_resolved,
                'space_saved_bytes': space_saved
            }
        }
        
        with open(self.project_root / 'DUPLICATE_RESOLUTION_REPORT.json', 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Full report: DUPLICATE_RESOLUTION_REPORT.json")
        print("=" * 60)

def main():
    """Main function"""
    project_root = "/workspaces/ZeroDev_AI"
    
    print("=" * 60)
    print("🔍 ZeroDev AI DUPLICATE RESOLVER")
    print("=" * 60)
    
    resolver = DuplicateResolver(project_root)
    resolver.resolve_duplicates()

if __name__ == "__main__":
    main()
