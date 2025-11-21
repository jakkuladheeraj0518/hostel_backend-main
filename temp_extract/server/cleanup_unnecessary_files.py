"""
Automated Cleanup Script
Removes all unnecessary files from the project
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Remove unnecessary files and directories"""
    
    print("=" * 80)
    print("PROJECT CLEANUP - REMOVING UNNECESSARY FILES")
    print("=" * 80)
    print()
    
    # Files to delete
    files_to_delete = [
        # Documentation/Report files
        "BUGFIX_RESOLVE_COMPLAINT.md",
        "CLEANUP_UNNECESSARY_FILES_LIST.md",
        "COMPLAINT_ASSIGNMENT_GUIDE.md",
        "COMPLAINT_RESOLUTION_GUIDE.md",
        "COMPLETE_ENDPOINT_TESTING_GUIDE.md",
        "ENDPOINT_DIAGNOSTICS_REPORT.md",
        "ENDPOINT_VERIFICATION_COMPLETE.md",
        "FINAL_PROJECT_STATUS.md",
        "FINAL_STATUS.txt",
        "FINAL_VERIFICATION_SUMMARY.md",
        "FULL_FUNCTIONALITY_CONFIRMED.md",
        "IMAGE_REQUIREMENTS_CHECKLIST.txt",
        "INTEGER_IDS_GUIDE.md",
        "MIGRATION_SUMMARY.txt",
        "PROJECT_CLEANUP_SUMMARY.md",
        "QUICK_ENDPOINT_STATUS.txt",
        "QUICK_START.md",
        "QUICK_TEST_REFERENCE.md",
        "QUICK_UPDATE_STEPS.md",
        "REQUIREMENTS_VERIFICATION.md",
        "ROLE_BASED_ASSIGNMENT_UPDATE.md",
        "SEED_DATA_VERIFICATION_REPORT.md",
        "SEQUENCE_VERIFICATION.md",
        "STRICT_IMAGE_BACKEND_VERIFICATION.md",
        "UPDATE_TO_INTEGER_IDS_GUIDE.md",
        
        # Test/Utility scripts
        "cleanup_project.py",
        "diagnose_endpoints.py",
        "get_supervisor_ids.py",
        "migrate_auto.py",
        "migrate_to_integer_ids.py",
        "run_seed_now.py",
        "test_all_endpoints.py",
        "test_auth.py",
        "test_leave_int_ids.py",
        "test_resolve_complaint.py",
        "test_role_assignment.py",
        "update_to_integer_ids.py",
        "verify_functionality.py",
        
        # Temporary files
        "seed_output.txt",
        "cleanup.bat",
        "cleanup.sh",
    ]
    
    # Directories to delete
    dirs_to_delete = [
        "__pycache__",
        "app/__pycache__",
        "app/api/__pycache__",
        "app/core/__pycache__",
        "app/models/__pycache__",
        "app/schemas/__pycache__",
        "alembic/__pycache__",
        "alembic/versions/__pycache__",
    ]
    
    deleted_files = 0
    deleted_dirs = 0
    errors = []
    
    # Delete files
    print("Deleting unnecessary files...")
    print("-" * 80)
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  ✓ Deleted: {file_path}")
                deleted_files += 1
            else:
                print(f"  - Skipped (not found): {file_path}")
        except Exception as e:
            error_msg = f"  ✗ Error deleting {file_path}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print()
    print("Deleting cache directories...")
    print("-" * 80)
    
    # Delete directories
    for dir_path in dirs_to_delete:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"  ✓ Deleted: {dir_path}/")
                deleted_dirs += 1
            else:
                print(f"  - Skipped (not found): {dir_path}/")
        except Exception as e:
            error_msg = f"  ✗ Error deleting {dir_path}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print()
    print("=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    print(f"Files deleted: {deleted_files}/{len(files_to_delete)}")
    print(f"Directories deleted: {deleted_dirs}/{len(dirs_to_delete)}")
    
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors:
            print(error)
    else:
        print("\n✅ Cleanup completed successfully!")
    
    print()
    print("=" * 80)
    print("REMAINING CORE FILES")
    print("=" * 80)
    
    core_files = [
        ".env",
        ".env.example",
        "alembic.ini",
        "docker-compose.yml",
        "Dockerfile",
        "hostel_management.db",
        "pytest.ini",
        "README.md",
        "requirements.txt",
        "reset_database.py",
        "run_seed.py",
        "run_server.py",
        "seed.py",
        "start_server.bat",
    ]
    
    for file in core_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (MISSING - may need attention)")
    
    print()
    print("=" * 80)
    print("PROJECT IS NOW CLEAN AND ORGANIZED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review remaining files")
    print("  2. Start server: python run_server.py")
    print("  3. Access docs: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    cleanup_project()
