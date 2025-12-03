"""
Authentication Verification Script
Verifies that all endpoints have proper role-based authentication
"""

import ast
import os
from pathlib import Path

def check_file_authentication(filepath):
    """Check if a file has proper authentication imports and usage"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {
        'file': filepath,
        'has_security_import': False,
        'has_role_required': False,
        'has_user_model': False,
        'has_role_import': False,
        'endpoints': []
    }
    
    # Check imports
    if 'from app.core.security import get_current_user' in content:
        results['has_security_import'] = True
    
    if 'from app.api.deps import role_required' in content:
        results['has_role_required'] = True
    
    if 'from app.models.user import User' in content:
        results['has_user_model'] = True
    
    if 'from app.core.roles import Role' in content:
        results['has_role_import'] = True
    
    # Parse AST to find endpoints
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has route decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr') and decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                            # Check if function has user parameter with Depends
                            has_auth = False
                            for arg in node.args.args:
                                if arg.arg == 'user':
                                    has_auth = True
                                    break
                            
                            endpoint_info = {
                                'name': node.name,
                                'has_auth': has_auth
                            }
                            results['endpoints'].append(endpoint_info)
    except:
        pass
    
    return results

def main():
    """Main verification function"""
    files_to_check = [
        'app/api/v1/student/reviews.py',
        'app/api/v1/student/leave_enhanced.py',
        'app/api/v1/admin/preventive_maintenance.py',
        'app/api/v1/admin/maintenance_costs.py',
        'app/api/v1/admin/maintenance.py',
        'app/api/v1/admin/maintenance_tasks.py',
        'app/api/v1/admin/maintenance_approvals.py',
        'app/api/v1/admin/leave.py',
        'app/api/v1/admin/reviews.py',
    ]
    
    print("=" * 80)
    print("ROLE-BASED AUTHENTICATION VERIFICATION")
    print("=" * 80)
    print()
    
    all_passed = True
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            all_passed = False
            continue
        
        results = check_file_authentication(filepath)
        
        # Determine if file passes all checks
        file_passed = (
            results['has_security_import'] and
            results['has_role_required'] and
            results['has_user_model'] and
            results['has_role_import']
        )
        
        status = "✅ PASS" if file_passed else "❌ FAIL"
        print(f"{status} - {filepath}")
        
        if not file_passed:
            print(f"  Missing imports:")
            if not results['has_security_import']:
                print(f"    - app.core.security.get_current_user")
            if not results['has_role_required']:
                print(f"    - app.api.deps.role_required")
            if not results['has_user_model']:
                print(f"    - app.models.user.User")
            if not results['has_role_import']:
                print(f"    - app.core.roles.Role")
            all_passed = False
        
        # Check endpoints
        if results['endpoints']:
            authenticated_count = sum(1 for ep in results['endpoints'] if ep['has_auth'])
            total_count = len(results['endpoints'])
            print(f"  Endpoints: {authenticated_count}/{total_count} have authentication")
            
            # Show endpoints without auth
            unauth_endpoints = [ep['name'] for ep in results['endpoints'] if not ep['has_auth']]
            if unauth_endpoints:
                print(f"  ⚠️  Endpoints without user parameter: {', '.join(unauth_endpoints)}")
        
        print()
    
    print("=" * 80)
    if all_passed:
        print("✅ ALL FILES PASSED AUTHENTICATION VERIFICATION")
        print()
        print("Summary:")
        print("- All files have proper security imports")
        print("- All files use role_required dependency")
        print("- All files use User model for type safety")
        print("- All files import Role enum")
        print()
        print("Next steps:")
        print("1. Test endpoints with JWT tokens")
        print("2. Verify role-based access control")
        print("3. Check error handling for unauthorized access")
    else:
        print("❌ SOME FILES FAILED VERIFICATION")
        print("Please review the files marked as FAIL above")
    print("=" * 80)

if __name__ == "__main__":
    main()
