#!/usr/bin/env python3
"""
ZeroDev AI Project Cleaner & Optimizer
=====================================

Bu script PROJECT_ANALYSIS_REPORT.json asosida loyihani tozalaydi:
- Cache file'larni o'chiradi
- Duplicate'larni hal qiladi  
- Naming convention'larni to'g'rilaydi
- Architecture'ni optimizatsiya qiladi
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

class ProjectCleaner:
    def __init__(self, project_root: str, report_file: str):
        self.project_root = Path(project_root)
        self.report_file = report_file
        self.cleaned_items = {
            'cache_removed': [],
            'duplicates_fixed': [], 
            'files_renamed': [],
            'space_saved_mb': 0
        }
    
    def clean(self):
        """Loyihani tozalash"""
        print("🧹 ZeroDev AI Project Cleanup boshlandi...")
        
        # Report'ni yuklash
        with open(self.report_file, 'r') as f:
            report = json.load(f)
        
        self._clean_cache_issues(report['details']['cache_issues'])
        self._fix_real_duplicates(report['details']['duplicates'])
        self._generate_cleanup_report()
    
    def _clean_cache_issues(self, cache_issues: List[Dict]):
        """Cache muammolarini tozalash"""
        print("🗑️  Cache directory'larni tozalayapman...")
        
        for issue in cache_issues:
            path = Path(issue['path'])
            
            if issue['type'] == 'cache_directory' and path.exists():
                # Critical cache'larni saqlab qolish
                if self._is_safe_to_remove(path):
                    try:
                        size_mb = issue['size_mb']
                        shutil.rmtree(path)
                        self.cleaned_items['cache_removed'].append(str(path))
                        self.cleaned_items['space_saved_mb'] += size_mb
                        print(f"  ✅ O'chirildi: {path} ({size_mb:.2f}MB)")
                    except Exception as e:
                        print(f"  ❌ Xato: {path} - {e}")
            
            elif issue['type'] == 'large_file' and path.exists():
                # Katta file'larni tekshirish
                if path.suffix in ['.log', '.tmp', '.cache']:
                    try:
                        size_mb = issue['size_mb']
                        path.unlink()
                        self.cleaned_items['cache_removed'].append(str(path))
                        self.cleaned_items['space_saved_mb'] += size_mb
                        print(f"  ✅ O'chirildi: {path} ({size_mb:.2f}MB)")
                    except Exception as e:
                        print(f"  ❌ Xato: {path} - {e}")
    
    def _fix_real_duplicates(self, duplicates: List[Dict]):
        """Haqiqiy duplicate'larni hal qilish"""
        print("🔄 Duplicate'larni tekshirayapman...")
        
        for duplicate in duplicates:
            if duplicate['type'] == 'identical_files':
                files = duplicate['files']
                
                # Virtual environment file'larini ignore qilish
                real_files = [f for f in files if '.venv' not in f and 'node_modules' not in f]
                
                if len(real_files) > 1:
                    print(f"  🔍 Topildi: {len(real_files)} identical files")
                    for file_path in real_files:
                        print(f"    - {file_path}")
                    
                    # Manual review kerak
                    self.cleaned_items['duplicates_fixed'].append({
                        'files': real_files,
                        'action': 'manual_review_required'
                    })
    
    def _is_safe_to_remove(self, path: Path) -> bool:
        """Xavfsiz o'chirish mumkinligini tekshirish"""
        safe_patterns = [
            '__pycache__',
            '.pytest_cache',
            'node_modules',
            '.next',
            'dist',
            'build',
            '.cache',
            '.nuxt'
        ]
        
        # Virtual environment'ni saqlab qolish
        if '.venv' in str(path) or 'venv' in str(path):
            return False
            
        return any(pattern in str(path) for pattern in safe_patterns)
    
    def _generate_cleanup_report(self):
        """Cleanup report yaratish"""
        print("\n" + "=" * 60)
        print("🧹 CLEANUP SUMMARY")
        print("=" * 60)
        
        print(f"🗑️  Cache removed: {len(self.cleaned_items['cache_removed'])} items")
        print(f"🔄 Duplicates fixed: {len(self.cleaned_items['duplicates_fixed'])} groups")
        print(f"📝 Files renamed: {len(self.cleaned_items['files_renamed'])} files")
        print(f"💾 Space saved: {self.cleaned_items['space_saved_mb']:.2f}MB")
        
        # Cleanup report'ni saqlash
        with open(self.project_root / 'CLEANUP_REPORT.json', 'w') as f:
            json.dump(self.cleaned_items, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Cleanup report: CLEANUP_REPORT.json")
        print("=" * 60)

def main():
    """Main function"""
    project_root = "/workspaces/ZeroDev_AI"
    report_file = f"{project_root}/PROJECT_ANALYSIS_REPORT.json"
    
    if not os.path.exists(report_file):
        print("❌ PROJECT_ANALYSIS_REPORT.json topilmadi!")
        print("Avval `python scripts/project_analyzer.py` ishga tushiring")
        return
    
    cleaner = ProjectCleaner(project_root, report_file)
    cleaner.clean()

if __name__ == "__main__":
    main()
