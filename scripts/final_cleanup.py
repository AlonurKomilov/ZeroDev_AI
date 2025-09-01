#!/usr/bin/env python3
"""
Final cleanup script to organize and clean the project
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def main():
    print("🧹 Final Project Cleanup")
    print("=" * 50)
    
    project_root = Path("/workspaces/ZeroDev_AI")
    
    # 1. Clean up generated reports
    print("\n1️⃣ Cleaning up analysis reports...")
    report_files = [
        "CLEANUP_REPORT.json",
        "DUPLICATE_ANALYSIS_REPORT.json", 
        "NAMING_FIXES_REPORT.json",
        "PROJECT_ANALYSIS_REPORT.json"
    ]
    
    cleaned_files = 0
    for report in report_files:
        report_path = project_root / report
        if report_path.exists():
            # Move to scripts folder for archival
            shutil.move(str(report_path), f"scripts/archived_{report}")
            cleaned_files += 1
            print(f"   📁 Archived {report}")
    
    # 2. Clean up cache files
    print("\n2️⃣ Cleaning up cache files...")
    cache_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/.pytest_cache",
        "**/node_modules", 
        "**/.next",
        "**/.venv"
    ]
    
    cache_cleaned = 0
    for pattern in cache_patterns:
        for path in project_root.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                cache_cleaned += 1
                print(f"   🗑️ Removed {path.relative_to(project_root)}")
    
    # 3. Validate file structure
    print("\n3️⃣ Validating project structure...")
    required_files = [
        "backend/security_engine/core.py",
        "backend/api/emergency.py", 
        "frontend/src/lib/auth.ts",
        "frontend/src/lib/api.ts",
        "frontend/src/contexts/AuthContext.tsx"
    ]
    
    all_valid = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.stat().st_size > 0:
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing or empty!")
            all_valid = False
    
    # 4. Summary
    print(f"\n📊 Cleanup Summary:")
    print(f"   📁 Reports archived: {cleaned_files}")
    print(f"   🗑️ Cache directories removed: {cache_cleaned}")
    print(f"   📋 File structure valid: {'✅ Yes' if all_valid else '❌ No'}")
    
    # 5. Create cleanup completion file
    completion_info = {
        "cleanup_date": datetime.now().isoformat(),
        "reports_archived": cleaned_files,
        "cache_cleaned": cache_cleaned, 
        "structure_valid": all_valid,
        "status": "completed"
    }
    
    with open(project_root / "scripts" / "cleanup_completion.json", "w") as f:
        json.dump(completion_info, f, indent=2)
    
    print(f"\n🎉 Final cleanup completed successfully!")
    print(f"📝 Completion report saved to scripts/cleanup_completion.json")

if __name__ == "__main__":
    main()
