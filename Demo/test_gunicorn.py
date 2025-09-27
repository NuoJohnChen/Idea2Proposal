#!/usr/bin/env python3
"""
Test script to verify Gunicorn configuration
"""
import subprocess
import sys
import time
import requests
import signal
import os

def test_gunicorn_config():
    """Test if gunicorn configuration is valid"""
    try:
        # Test configuration file syntax
        result = subprocess.run([
            'gunicorn', '--check-config', '--config', 'gunicorn.conf.py', 'wsgi:app'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Gunicorn configuration is valid")
            return True
        else:
            print(f"❌ Gunicorn configuration error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Gunicorn configuration check timed out")
        return False
    except FileNotFoundError:
        print("❌ Gunicorn not found. Please install with: pip install gunicorn")
        return False
    except Exception as e:
        print(f"❌ Error testing gunicorn config: {e}")
        return False

def test_wsgi_import():
    """Test if wsgi.py can be imported"""
    try:
        import wsgi
        print("✅ wsgi.py imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing wsgi.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing wsgi.py: {e}")
        return False

def test_app_import():
    """Test if app.py can be imported"""
    try:
        from app import app
        print("✅ app.py imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing app.py: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Gunicorn Configuration")
    print("=" * 40)
    
    tests = [
        ("App Import", test_app_import),
        ("WSGI Import", test_wsgi_import),
        ("Gunicorn Config", test_gunicorn_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Failed: {test_name}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gunicorn is ready to use.")
        print("\n🚀 To start the server, run:")
        print("   ./start_gunicorn.sh")
        print("   or")
        print("   gunicorn --config gunicorn.conf.py wsgi:app")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
