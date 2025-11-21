"""Wrapper to run seed.py with better error handling"""
import sys
import traceback

try:
    print("Starting seed script...")
    print("="*60)
    
    # Import and run the main function from seed.py
    from seed import main
    main()
    
    print("\n" + "="*60)
    print("✅ SEED SCRIPT COMPLETED SUCCESSFULLY!")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ ERROR OCCURRED:")
    print("="*60)
    print(f"\nError: {str(e)}\n")
    traceback.print_exc()
    sys.exit(1)
