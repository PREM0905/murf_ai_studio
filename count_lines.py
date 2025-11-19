import os
import glob

def count_lines_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0

def count_project_lines():
    project_root = r"c:\Users\Yash\OneDrive\Desktop\STUDIO_IITB"
    
    # File extensions to count
    extensions = ['*.py', '*.js', '*.html', '*.css', '*.md']
    
    total_lines = 0
    file_counts = {}
    
    for ext in extensions:
        file_counts[ext] = {'files': 0, 'lines': 0}
    
    # Walk through project directory
    for root, dirs, files in os.walk(project_root):
        # Skip virtual environment and cache directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            # Check if file matches our extensions
            for ext in extensions:
                if file.endswith(ext[1:]):  # Remove * from extension
                    lines = count_lines_in_file(filepath)
                    file_counts[ext]['files'] += 1
                    file_counts[ext]['lines'] += lines
                    total_lines += lines
                    print(f"{filepath}: {lines} lines")
                    break
    
    print("\n" + "="*60)
    print("STUDIO PROJECT - LINE COUNT SUMMARY")
    print("="*60)
    
    for ext, data in file_counts.items():
        if data['files'] > 0:
            print(f"{ext.upper():<8}: {data['files']:>3} files, {data['lines']:>5} lines")
    
    print("-"*60)
    print(f"TOTAL   : {sum(data['files'] for data in file_counts.values()):>3} files, {total_lines:>5} lines")
    print("="*60)

if __name__ == "__main__":
    count_project_lines()