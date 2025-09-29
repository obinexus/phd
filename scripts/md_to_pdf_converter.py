#!/usr/bin/env python3
"""
Markdown to PDF Converter with LaTeX Support
Converts all .md files in a directory to PDFs and creates a zip archive
"""

import os
import sys
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required tools are installed"""
    required = {
        'pandoc': 'pandoc --version',
        'pdflatex': 'pdflatex --version'
    }
    
    missing = []
    for tool, cmd in required.items():
        try:
            subprocess.run(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print("ERROR: Missing required dependencies:")
        for tool in missing:
            print(f"  - {tool}")
        print("\nInstall with:")
        print("  Ubuntu/Debian: sudo apt-get install pandoc texlive-full")
        print("  macOS: brew install pandoc basictex")
        print("  Windows: Install MiKTeX and Pandoc from their websites")
        return False
    return True

def convert_md_to_pdf(md_file, output_dir):
    """Convert a single Markdown file to PDF using pandoc"""
    md_path = Path(md_file)
    pdf_path = output_dir / md_path.with_suffix('.pdf').name
    
    print(f"Converting: {md_path.name} -> {pdf_path.name}")
    
    # Pandoc command with LaTeX equation support
    cmd = [
        'pandoc',
        str(md_path),
        '-o', str(pdf_path),
        '--pdf-engine=pdflatex',
        '--variable', 'geometry:margin=1in',
        '--variable', 'fontsize=11pt',
        '--variable', 'colorlinks=true',
        '--variable', 'linkcolor=blue',
        '--toc',  # Table of contents
        '--toc-depth=3',
        '--number-sections',
        '-V', 'papersize=a4'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per file
        )
        
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr}")
            return False
        
        print(f"  SUCCESS: Created {pdf_path.name}")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  ERROR: Conversion timed out")
        return False
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return False

def create_zip_archive(pdf_dir, output_zip):
    """Create a zip archive of all PDFs"""
    print(f"\nCreating zip archive: {output_zip}")
    
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("ERROR: No PDF files to archive")
        return False
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pdf_file in pdf_files:
            zipf.write(pdf_file, pdf_file.name)
            print(f"  Added: {pdf_file.name}")
    
    print(f"SUCCESS: Created {output_zip}")
    print(f"Archive contains {len(pdf_files)} PDF files")
    return True

def main():
    """Main conversion pipeline"""
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <markdown_directory> [output_zip_name]")
        print("\nExample:")
        print("  python md_to_pdf.py ~/obinexus/workspace/phd")
        print("  python md_to_pdf.py ~/obinexus/workspace/phd phd_documents.zip")
        sys.exit(1)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Parse arguments
    input_dir = Path(sys.argv[1]).expanduser().resolve()
    
    if len(sys.argv) >= 3:
        output_zip_name = sys.argv[2]
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_zip_name = f"phd_documents_{timestamp}.zip"
    
    # Validate input directory
    if not input_dir.exists():
        print(f"ERROR: Directory does not exist: {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"ERROR: Not a directory: {input_dir}")
        sys.exit(1)
    
    # Find all markdown files
    md_files = list(input_dir.glob('*.md'))
    
    if not md_files:
        print(f"ERROR: No .md files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(md_files)} Markdown files")
    print(f"Input directory: {input_dir}")
    print(f"Output zip: {output_zip_name}\n")
    
    # Create output directory for PDFs
    output_dir = input_dir / 'pdf_output'
    output_dir.mkdir(exist_ok=True)
    
    # Convert all markdown files
    success_count = 0
    failed_files = []
    
    for md_file in md_files:
        if convert_md_to_pdf(md_file, output_dir):
            success_count += 1
        else:
            failed_files.append(md_file.name)
    
    print(f"\nConversion complete: {success_count}/{len(md_files)} successful")
    
    if failed_files:
        print("\nFailed conversions:")
        for filename in failed_files:
            print(f"  - {filename}")
    
    # Create zip archive
    output_zip = input_dir / output_zip_name
    if create_zip_archive(output_dir, output_zip):
        print(f"\nFinal output: {output_zip}")
        print(f"Size: {output_zip.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print("\nERROR: Failed to create zip archive")
        sys.exit(1)

if __name__ == "__main__":
    main()
