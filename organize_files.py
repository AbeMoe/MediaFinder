#!/usr/bin/env python3
"""
Media & Document Organizer with Symbolic Links
Scans the computer for pictures, audio, video, and text files,
then creates symbolic links organized by category.
"""

import os
import sys
import string
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
import argparse

# File extensions by category
FILE_CATEGORIES = {
    'pictures': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif', '.ico', '.heic', '.raw'},
    'audio': {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.opus', '.ape', '.alac'},
    'video': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'},
    'text': {'.txt', '.pdf', '.doc', '.docx', '.rtf', '.odt', '.md', '.epub', '.mobi'}
}

# Directories to exclude (case-insensitive)
EXCLUDED_DIRS = {
    # Windows system directories
    'windows', 'program files', 'program files (x86)', 'programdata',
    '$recycle.bin', 'system volume information', '$windows.~bt', '$windows.~ws',
    'recovery', 'boot', 'msocache', 'perflogs',

    # AppData and temp
    'appdata', 'temp', 'tmp', 'cache', 'caches',

    # Development folders
    'node_modules', 'venv', '__pycache__', '.venv', 'env',
    'build', 'dist', '.next', '.nuxt', 'target',

    # Version control
    '.git', '.svn', '.hg',

    # Other hidden/system
    '.cache', '.config', '.vscode', '.idea'
}


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_all_drives():
    """Get all available drive letters on Windows."""
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def should_exclude_directory(path: Path) -> bool:
    """
    Check if a directory should be excluded from scanning.

    Args:
        path: Path object to check

    Returns:
        True if directory should be excluded, False otherwise
    """
    # Check if it's a hidden folder (starts with .)
    if path.name.startswith('.'):
        return True

    # Check against excluded directories (case-insensitive)
    path_lower = path.name.lower()
    if path_lower in EXCLUDED_DIRS:
        return True

    # Check if any parent directory is in excluded list
    try:
        parts_lower = [p.lower() for p in path.parts]
        for excluded in EXCLUDED_DIRS:
            if excluded in parts_lower:
                return True
    except:
        pass

    return False


def get_file_category(file_path: Path) -> str:
    """
    Determine the category of a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        Category name or None if file doesn't match any category
    """
    extension = file_path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return None


def scan_for_files(drives: List[str], progress_callback=None) -> Dict[str, List[Path]]:
    """
    Scan specified drives for media and document files.

    Args:
        drives: List of drive letters to scan
        progress_callback: Optional callback function for progress updates

    Returns:
        Dictionary mapping categories to lists of file paths
    """
    found_files = defaultdict(list)
    scanned_count = 0
    skipped_count = 0

    print(f"\nScanning {len(drives)} drive(s)...")

    for drive in drives:
        print(f"\n  Scanning drive: {drive}")

        try:
            for root, dirs, files in os.walk(drive):
                # Convert to Path object
                root_path = Path(root)

                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not should_exclude_directory(root_path / d)]

                # Check files in current directory
                for file in files:
                    file_path = root_path / file

                    # Skip if it's a system file
                    try:
                        if file_path.stat().st_file_attributes & 0x4:  # FILE_ATTRIBUTE_SYSTEM
                            skipped_count += 1
                            continue
                    except (AttributeError, OSError):
                        pass  # stat().st_file_attributes not available on all systems

                    # Categorize file
                    category = get_file_category(file_path)
                    if category:
                        found_files[category].append(file_path)
                        scanned_count += 1

                        if progress_callback and scanned_count % 100 == 0:
                            progress_callback(scanned_count, category, file_path)

        except PermissionError:
            print(f"    [Skipped: Permission denied]")
            continue
        except Exception as e:
            print(f"    [Error: {str(e)}]")
            continue

    print(f"\n  Scan complete! Found {scanned_count} files across {len(found_files)} categories")
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} system files")

    return dict(found_files)


def create_hybrid_structure(category: str, source_file: Path, base_output_dir: Path, dry_run: bool = False) -> Path:
    """
    Create a hybrid folder structure for organizing symbolic links.

    Args:
        category: File category (pictures, audio, video, text)
        source_file: Original file path
        base_output_dir: Base directory for output
        dry_run: If True, don't actually create directories

    Returns:
        Target path for the symbolic link
    """
    # Get the parent directory name of the source file
    # This creates a subfolder structure like: pictures/Documents/photo.jpg
    try:
        # Get a meaningful parent folder name
        parent_name = source_file.parent.name
        if not parent_name or parent_name == '\\' or parent_name == '/':
            parent_name = source_file.drive.replace(':', '').replace('\\', '')
    except:
        parent_name = 'root'

    # Create category/parent structure
    target_dir = base_output_dir / category / parent_name
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    # Handle duplicate filenames
    target_path = target_dir / source_file.name
    counter = 1
    while target_path.exists():
        stem = source_file.stem
        suffix = source_file.suffix
        target_path = target_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    return target_path


def create_symbolic_links(files_by_category: Dict[str, List[Path]],
                         output_dir: Path,
                         dry_run: bool = False) -> Dict[str, int]:
    """
    Create symbolic links for all found files.

    Args:
        files_by_category: Dictionary mapping categories to file lists
        output_dir: Base directory for symbolic links
        dry_run: If True, only simulate without creating actual links

    Returns:
        Dictionary with statistics about created links
    """
    stats = {
        'created': 0,
        'failed': 0,
        'skipped': 0
    }

    mode = "DRY RUN" if dry_run else "CREATING LINKS"
    print(f"\n{mode}: Organizing files into {output_dir}")

    for category, files in files_by_category.items():
        print(f"\n  [{category.upper()}] Processing {len(files)} files...")

        for source_file in files:
            try:
                # Determine target path with hybrid structure
                target_path = create_hybrid_structure(category, source_file, output_dir, dry_run)

                if dry_run:
                    print(f"    Would link: {source_file} -> {target_path}")
                    stats['created'] += 1
                else:
                    # Create symbolic link
                    os.symlink(source_file, target_path)
                    stats['created'] += 1

                    # Progress indicator
                    if stats['created'] % 50 == 0:
                        print(f"    Created {stats['created']} links...")

            except FileExistsError:
                stats['skipped'] += 1
            except OSError as e:
                print(f"    Failed to link {source_file.name}: {str(e)}")
                stats['failed'] += 1
            except Exception as e:
                print(f"    Unexpected error with {source_file.name}: {str(e)}")
                stats['failed'] += 1

    return stats


def print_summary(files_by_category: Dict[str, List[Path]], stats: Dict[str, int], dry_run: bool):
    """Print a summary of the operation."""
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print("\nFiles found by category:")
    for category, files in sorted(files_by_category.items()):
        print(f"  {category.capitalize()}: {len(files)} files")

    print(f"\nTotal files found: {sum(len(files) for files in files_by_category.values())}")

    if dry_run:
        print(f"\nDRY RUN complete - no actual links were created")
        print(f"  Would create: {stats['created']} links")
    else:
        print(f"\nSymbolic links created: {stats['created']}")

    if stats['failed'] > 0:
        print(f"Failed: {stats['failed']}")
    if stats['skipped'] > 0:
        print(f"Skipped (already exist): {stats['skipped']}")

    print("="*70)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Organize media and documents with symbolic links',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python organize_files.py --dry-run          # Preview what will be linked
  python organize_files.py                     # Create symbolic links
  python organize_files.py --output ./media    # Custom output directory
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without creating actual symbolic links'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='.',
        help='Output directory for organized folders (default: current directory)'
    )

    parser.add_argument(
        '--drives',
        type=str,
        nargs='+',
        help='Specific drives to scan (e.g., C: D:), default: all drives'
    )

    args = parser.parse_args()

    # Print header
    print("="*70)
    print("MEDIA & DOCUMENT ORGANIZER")
    print("="*70)

    # Check for admin privileges
    if not is_admin():
        print("\nWARNING: Not running as administrator!")
        print("Symbolic link creation may fail on some Windows versions.")
        print("Consider running this script as administrator.\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

    # Get drives to scan
    if args.drives:
        drives = [d if d.endswith(':\\') else f"{d}:\\" for d in args.drives]
    else:
        drives = get_all_drives()

    print(f"\nDrives to scan: {', '.join(drives)}")

    # Set up output directory
    output_dir = Path(args.output).resolve()
    print(f"Output directory: {output_dir}")

    if not args.dry_run:
        print("\nThis will create symbolic links on your system.")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

    # Progress callback
    def progress(count, category, file_path):
        print(f"    Found {count} files... (last: {category}/{file_path.name})")

    # Scan for files
    files_by_category = scan_for_files(drives, progress_callback=progress)

    if not files_by_category:
        print("\nNo files found matching the specified categories.")
        sys.exit(0)

    # Create symbolic links
    stats = create_symbolic_links(files_by_category, output_dir, dry_run=args.dry_run)

    # Print summary
    print_summary(files_by_category, stats, args.dry_run)

    if args.dry_run:
        print("\nTo create the symbolic links for real, run without --dry-run flag")


if __name__ == '__main__':
    main()
