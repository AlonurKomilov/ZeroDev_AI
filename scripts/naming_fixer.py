#!/usr/bin/env python3
"""
ZeroDev AI Naming Convention Fixer
=================================

Bu script naming convention'larni to'g'rilaydi:
- Python files: snake_case
- TypeScript/JS files: camelCase yoki kebab-case
- Directory names: lowercase
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict

class NamingFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.skipped_files = []
    
    def fix_naming_issues(self):
        """Naming issues'ni to'g'rilash"""
        print("📝 Naming convention'larni to'g'irlayapman...")
        
        # Python files
        self._fix_python_naming()
        
        # TypeScript/JS files  
        self._fix_js_naming()
        
        # Directory names
        self._fix_directory_naming()
        
        self._generate_report()
    
    def _fix_python_naming(self):
        """Python file naming'ni to'g'rilash"""
        print("🐍 Python files'ni tekshirayapman...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            filename = py_file.stem
            
            # snake_case'ga o'tkazish kerak bo'lgan file'lar
            if not re.match(r'^[a-z][a-z0-9_]*$', filename) and filename != '__init__':
                new_name = self._to_snake_case(filename)
                new_path = py_file.parent / f"{new_name}.py"
                
                if not new_path.exists() and new_name != filename:
                    try:
                        py_file.rename(new_path)
                        self.fixes_applied.append({
                            'type': 'python_rename',
                            'old': str(py_file),
                            'new': str(new_path),
                            'change': f"{filename} → {new_name}"
                        })
                        print(f"  ✅ Renamed: {filename} → {new_name}")
                    except Exception as e:
                        self.skipped_files.append({
                            'file': str(py_file),
                            'reason': str(e)
                        })
    
    def _fix_js_naming(self):
        """JavaScript/TypeScript file naming'ni to'g'rilash"""
        print("🟨 TypeScript/JS files'ni tekshirayapman...")
        
        js_files = (
            list(self.project_root.rglob("*.tsx")) + 
            list(self.project_root.rglob("*.ts")) + 
            list(self.project_root.rglob("*.js"))
        )
        
        for js_file in js_files:
            if self._should_skip_file(js_file):
                continue
                
            filename = js_file.stem
            
            # Agar camelCase yoki kebab-case emas bo'lsa
            if not re.match(r'^[a-z][a-zA-Z0-9]*$|^[a-z][a-z0-9-]*$', filename):
                # kebab-case'ga o'tkazish
                new_name = self._to_kebab_case(filename)
                new_path = js_file.parent / f"{new_name}{js_file.suffix}"
                
                if not new_path.exists() and new_name != filename:
                    try:
                        js_file.rename(new_path)
                        self.fixes_applied.append({
                            'type': 'js_rename',
                            'old': str(js_file),
                            'new': str(new_path),
                            'change': f"{filename} → {new_name}"
                        })
                        print(f"  ✅ Renamed: {filename} → {new_name}")
                    except Exception as e:
                        self.skipped_files.append({
                            'file': str(js_file),
                            'reason': str(e)
                        })
    
    def _fix_directory_naming(self):
        """Directory naming'ni to'g'rilash"""
        print("📁 Directory names'ni tekshirayapman...")
        
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and self._should_skip_file(dir_path):
                continue
                
            if dir_path.is_dir():
                dir_name = dir_path.name
                
                # Lowercase va kebab-case'ga o'tkazish
                if not re.match(r'^[a-z][a-z0-9-]*$', dir_name):
                    new_name = self._to_kebab_case(dir_name)
                    new_path = dir_path.parent / new_name
                    
                    if not new_path.exists() and new_name != dir_name:
                        try:
                            dir_path.rename(new_path)
                            self.fixes_applied.append({
                                'type': 'directory_rename',
                                'old': str(dir_path),
                                'new': str(new_path),
                                'change': f"{dir_name} → {new_name}"
                            })
                            print(f"  ✅ Directory renamed: {dir_name} → {new_name}")
                        except Exception as e:
                            self.skipped_files.append({
                                'file': str(dir_path),
                                'reason': str(e)
                            })
    
    def _to_snake_case(self, text: str) -> str:
        """String'ni snake_case'ga o'tkazish"""
        # CamelCase'dan snake_case'ga
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        # Special characters'ni _ bilan almashtirish
        s3 = re.sub(r'[^a-z0-9_]', '_', s2)
        
        # Multiple _ larni bitta _'ga aylantirish
        s4 = re.sub(r'_+', '_', s3)
        
        # Boshlanish va tugashdan _'ni olib tashlash
        return s4.strip('_')
    
    def _to_kebab_case(self, text: str) -> str:
        """String'ni kebab-case'ga o'tkazish"""
        # CamelCase'dan kebab-case'ga
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
        
        # Special characters'ni - bilan almashtirish
        s3 = re.sub(r'[^a-z0-9-]', '-', s2)
        
        # Multiple - larni bitta -'ga aylantirish
        s4 = re.sub(r'-+', '-', s3)
        
        # Boshlanish va tugashdan -'ni olib tashlash
        return s4.strip('-')
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Skip qilinadigan file'lar"""
        skip_patterns = [
            '.venv',
            'node_modules', 
            '.git',
            '__pycache__',
            '.next',
            'dist',
            'build',
            '.pytest_cache'
        ]
        
        str_path = str(file_path)
        return any(pattern in str_path for pattern in skip_patterns)
    
    def _generate_report(self):
        """Report yaratish"""
        print("\n" + "=" * 60)
        print("📝 NAMING CONVENTION FIXES SUMMARY")  
        print("=" * 60)
        
        fixes_by_type = {}
        for fix in self.fixes_applied:
            fix_type = fix['type']
            if fix_type not in fixes_by_type:
                fixes_by_type[fix_type] = 0
            fixes_by_type[fix_type] += 1
        
        print(f"✅ Jami fixes: {len(self.fixes_applied)}")
        for fix_type, count in fixes_by_type.items():
            print(f"  {fix_type}: {count}")
        
        print(f"⏭️  Skipped files: {len(self.skipped_files)}")
        
        # Report'ni saqlash
        report = {
            'fixes_applied': self.fixes_applied,
            'skipped_files': self.skipped_files,
            'summary': fixes_by_type
        }
        
        with open(self.project_root / 'NAMING_FIXES_REPORT.json', 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Naming fixes report: NAMING_FIXES_REPORT.json")
        print("=" * 60)

def main():
    """Main function"""
    project_root = "/workspaces/ZeroDev_AI"
    
    print("=" * 60)
    print("📝 ZeroDev AI NAMING CONVENTION FIXER")
    print("=" * 60)
    
    fixer = NamingFixer(project_root)
    fixer.fix_naming_issues()

if __name__ == "__main__":
    main()
