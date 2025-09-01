#!/usr/bin/env python3
"""
Professional Emergency Panel Verification (Playwright-free)
Uses the professional verifier without external dependencies
"""

import sys
import os
from pathlib import Path

# Add tools directory to path
sys.path.append('/workspaces/ZeroDev_AI/tools')

try:
    from professional_emergency_verifier import ProfessionalEmergencyVerifier
    
    def main():
        """Run professional verification"""
        print("🛡️  Running Professional Emergency Panel Verification...")
        
        verifier = ProfessionalEmergencyVerifier()
        results = verifier.verify_emergency_panel()
        
        # Generate report
        report_path = verifier.generate_report(results)
        
        # Print summary
        print(f"\n📊 Verification Status: {results['overall_status'].upper()}")
        print(f"⏱️  Time: {results['verification_time']:.2f}s")
        print(f"📄 Report: {report_path}")
        
        return 0 if results['overall_status'] == 'passed' else 1
        
except ImportError:
    print("⚠️  Professional verifier not available, using simple verification...")
    
    def verify_simple():
        """Simple file existence verification"""
        emergency_path = Path('/workspaces/ZeroDev_AI/emergency-panel-app')
        
        files_to_check = [
            'index.html',
            'index_enhanced.html', 
            'script.js',
            'script-enhanced.js',
            'styles.css'
        ]
        
        print("🔍 Verifying Emergency Panel Files...")
        
        all_exist = True
        for file_name in files_to_check:
            file_path = emergency_path / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✅ {file_name}: {size:,} bytes")
            else:
                print(f"❌ {file_name}: NOT FOUND")
                all_exist = False
        
        print(f"\n📊 Verification: {'PASSED' if all_exist else 'FAILED'}")
        return 0 if all_exist else 1
    
    def main():
        return verify_simple()

if __name__ == "__main__":
    sys.exit(main())
