# Media & Document Organizer

A Python script that scans your computer for pictures, audio, video, and text files, then organizes them using symbolic links in categorized folders.

## Features

- Scans all drives on your computer (or specific drives)
- Organizes files into 4 categories: pictures, audio, video, and text
- Creates symbolic links (not copies) to save disk space
- Uses hybrid folder structure to avoid naming conflicts
- Skips system files and common development/cache folders
- Includes dry-run mode to preview changes before applying
- Progress indicators and detailed summary reports
- Windows-compatible with admin privilege detection

## Supported File Types

### Pictures
`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`, `.tiff`, `.tif`, `.ico`, `.heic`, `.raw`

### Audio
`.mp3`, `.wav`, `.flac`, `.m4a`, `.aac`, `.ogg`, `.wma`, `.opus`, `.ape`, `.alac`

### Video
`.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`, `.3gp`

### Text Documents
`.txt`, `.pdf`, `.doc`, `.docx`, `.rtf`, `.odt`, `.md`, `.epub`, `.mobi`

## Installation

No installation required! Just ensure you have Python 3.6+ installed.

## Usage

### Basic Usage (Dry Run - Recommended First Step)

```bash
python organize_files.py --dry-run
```

This will scan your computer and show you what would be linked WITHOUT actually creating any symbolic links.

### Create Symbolic Links

```bash
python organize_files.py
```

This will create the symbolic links in the current directory.

### Custom Output Directory

```bash
python organize_files.py --output C:\MyOrganizedFiles
```

### Scan Specific Drives Only

```bash
python organize_files.py --drives C: D:
```

### Get Help

```bash
python organize_files.py --help
```

## Output Structure

The script creates a hybrid folder structure:

```
output_directory/
├── pictures/
│   ├── Documents/
│   │   └── vacation_photo.jpg -> C:\Users\YourName\Documents\vacation_photo.jpg
│   ├── Downloads/
│   │   └── screenshot.png -> C:\Users\YourName\Downloads\screenshot.png
│   └── Pictures/
│       └── family.jpg -> C:\Users\YourName\Pictures\family.jpg
├── audio/
│   ├── Music/
│   │   ├── song1.mp3 -> C:\Users\YourName\Music\song1.mp3
│   │   └── song2.mp3 -> C:\Users\YourName\Music\song2.mp3
│   └── Downloads/
│       └── podcast.mp3 -> C:\Users\YourName\Downloads\podcast.mp3
├── video/
│   └── Videos/
│       └── movie.mp4 -> C:\Users\YourName\Videos\movie.mp4
└── text/
    ├── Documents/
    │   ├── report.pdf -> C:\Users\YourName\Documents\report.pdf
    │   └── notes.txt -> C:\Users\YourName\Documents\notes.txt
    └── Downloads/
        └── ebook.pdf -> C:\Users\YourName\Downloads\ebook.pdf
```

Each file is organized by:
1. **Category** (pictures, audio, video, text)
2. **Source folder name** (to avoid conflicts and maintain context)
3. **Original filename**

## What Gets Skipped

The script automatically excludes:

### Hidden Folders
- Folders starting with `.` (like `.git`, `.cache`, etc.)

### Windows System Directories
- `Windows`, `Program Files`, `ProgramData`
- `$Recycle.Bin`, `System Volume Information`
- `Recovery`, `Boot`, etc.

### AppData & Temporary Files
- `AppData`, `Temp`, `Cache`

### Development Folders
- `node_modules`, `venv`, `__pycache__`
- `build`, `dist`, `.next`, `target`

## Important Notes

### Administrator Privileges

On some Windows versions, creating symbolic links requires administrator privileges. The script will:
1. Check if you're running as admin
2. Warn you if you're not
3. Ask if you want to continue anyway

To run as administrator:
1. Right-click Command Prompt or PowerShell
2. Select "Run as administrator"
3. Navigate to the script directory
4. Run the script

### Developer Mode (Windows 10/11)

Alternatively, enable Developer Mode in Windows:
1. Settings > Update & Security > For developers
2. Enable "Developer Mode"
3. No admin privileges needed after this

### Symbolic Links vs Copies

This script creates **symbolic links**, not copies:
- No additional disk space is used
- If you delete the original file, the link will break
- If you modify the file through the link, the original file changes
- If you move the original file, the link will break

### Disk Space

The script will scan ALL drives, which can take a significant amount of time on:
- Large hard drives
- Network drives
- External drives

Consider using the `--drives` option to scan specific drives only.

## Examples

### Preview before creating links
```bash
python organize_files.py --dry-run
```

### Organize files in a custom location
```bash
python organize_files.py --output "D:\Organized Media"
```

### Scan only C: drive
```bash
python organize_files.py --drives C:
```

### Scan C: and D: drives with dry-run
```bash
python organize_files.py --drives C: D: --dry-run
```

## Troubleshooting

### "Permission denied" errors
- Run the script as administrator
- Or enable Developer Mode on Windows 10/11

### Links not working
- Make sure the original files haven't been moved or deleted
- Verify symbolic links are supported on your file system

### Script is very slow
- Large drives take time to scan
- Use `--drives` to scan specific drives only
- Excluded directories should help, but some folders may have many files

### Too many files found
- Check the dry-run output first
- The hybrid structure helps organize files by source folder
- You can modify the `FILE_CATEGORIES` in the script to be more selective

## Safety

This script is designed to be safe:
- It never deletes or modifies original files
- It only creates symbolic links
- Dry-run mode lets you preview changes
- It requires confirmation before creating links
- It skips system files and directories

## License

Free to use and modify as needed.
