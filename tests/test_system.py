"""Simple test script to verify the Manarah system is working."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings

def test_configuration():
    """Test that configuration is loaded correctly."""
    print("🔧 Testing Configuration...")
    
    try:
        assert settings.openai_api_key, "OpenAI API key not set"
        assert settings.api_port == 8000, "API port mismatch"
        assert settings.frame_extraction_fps == 15, "FPS mismatch"
        print("✅ Configuration loaded successfully")
        print(f"   - API Port: {settings.api_port}")
        print(f"   - FPS: {settings.frame_extraction_fps}")
        print(f"   - OpenAI Key: {'*' * 10}{settings.openai_api_key[-4:]}")
        return True
    except AssertionError as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_directories():
    """Test that required directories exist."""
    print("\n📁 Testing Directories...")
    
    required_dirs = [
        settings.data_dir,
        settings.content_dir,
        settings.analysis_dir,
        settings.decisions_dir,
        settings.audit_dir
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path.name}/ exists")
        else:
            print(f"❌ {dir_path.name}/ missing")
            all_exist = False
    
    return all_exist


def test_imports():
    """Test that all modules can be imported."""
    print("\n📦 Testing Module Imports...")
    
    modules = [
        ("src.storage", "Storage"),
        ("src.preprocessor", "Content Preprocessor"),
        ("src.vision_analyzer", "Vision Analyzer"),
        ("src.text_analyzer", "Text Analyzer"),
        ("src.decision_engine", "Decision Engine"),
        ("src.main", "FastAPI App")
    ]
    
    all_imported = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name} imported successfully")
        except Exception as e:
            print(f"❌ {display_name} import failed: {e}")
            all_imported = False
    
    return all_imported


def test_ffmpeg():
    """Test that FFmpeg is available."""
    print("\n🎬 Testing FFmpeg...")
    
    try:
        import ffmpeg
        print("✅ FFmpeg Python package installed")
        
        # Try to get FFmpeg version
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg binary found: {version_line}")
            return True
        else:
            print("❌ FFmpeg binary not found in PATH")
            return False
    except ImportError:
        print("❌ FFmpeg Python package not installed")
        return False
    except FileNotFoundError:
        print("❌ FFmpeg binary not found. Install from: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ FFmpeg test failed: {e}")
        return False


def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Simple API test
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say 'test successful' in exactly 2 words."}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API connected successfully")
        print(f"   Response: {result}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("   Check your OPENAI_API_KEY in .env file")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Manarah System Test Suite")
    print("=" * 60)
    
    results = {
        "Configuration": test_configuration(),
        "Directories": test_directories(),
        "Module Imports": test_imports(),
        "FFmpeg": test_ffmpeg(),
        "OpenAI API": test_openai_connection()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed! System is ready.")
        print("\n🚀 Start the server with:")
        print("   python -m uvicorn src.main:app --reload --port 8000")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
