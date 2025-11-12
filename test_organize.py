#!/usr/bin/env python3
"""
Quick test script to verify organize_files.py functions work correctly
"""

from pathlib import Path
import organize_files

def test_file_categorization():
    """Test that file extensions are correctly categorized."""
    print("Testing file categorization...")

    test_cases = {
        'photo.jpg': 'pictures',
        'song.mp3': 'audio',
        'movie.mp4': 'video',
        'document.pdf': 'text',
        'unknown.xyz': None
    }

    for filename, expected_category in test_cases.items():
        path = Path(filename)
        category = organize_files.get_file_category(path)
        status = "[PASS]" if category == expected_category else "[FAIL]"
        print(f"  {status} {filename} -> {category} (expected: {expected_category})")
        assert category == expected_category, f"Failed for {filename}"

    print("  All categorization tests passed!\n")


def test_directory_exclusion():
    """Test that system directories are correctly excluded."""
    print("Testing directory exclusion...")

    test_cases = [
        (Path('C:/Windows/System32'), True),
        (Path('C:/Program Files'), True),
        (Path('C:/Users/Abe/.cache'), True),
        (Path('C:/Users/Abe/node_modules'), True),
        (Path('C:/Users/Abe/Documents'), False),
        (Path('C:/Users/Abe/Pictures'), False),
    ]

    for path, should_exclude in test_cases:
        is_excluded = organize_files.should_exclude_directory(path)
        status = "[PASS]" if is_excluded == should_exclude else "[FAIL]"
        print(f"  {status} {path} -> excluded={is_excluded} (expected: {should_exclude})")
        assert is_excluded == should_exclude, f"Failed for {path}"

    print("  All exclusion tests passed!\n")


def test_drive_detection():
    """Test that drives can be detected."""
    print("Testing drive detection...")

    drives = organize_files.get_all_drives()
    print(f"  Found drives: {', '.join(drives)}")
    assert len(drives) > 0, "No drives found"
    assert 'C:\\' in drives, "C: drive not found"

    print("  Drive detection passed!\n")


def test_admin_check():
    """Test admin privilege detection."""
    print("Testing admin privilege check...")

    is_admin = organize_files.is_admin()
    print(f"  Running as admin: {is_admin}")
    print("  Admin check completed!\n")


if __name__ == '__main__':
    print("="*70)
    print("ORGANIZE FILES - UNIT TESTS")
    print("="*70 + "\n")

    try:
        test_file_categorization()
        test_directory_exclusion()
        test_drive_detection()
        test_admin_check()

        print("="*70)
        print("ALL TESTS PASSED!")
        print("="*70)

    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        exit(1)
