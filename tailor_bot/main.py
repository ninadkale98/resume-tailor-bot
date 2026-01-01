import os
import sys
import shutil
import subprocess
from datetime import datetime
from prompts import TAILOR_PROMPT
from llm_client import LLMClient

# Configuration
DIRS_TO_PROCESS = ['experience', 'projects']
JD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'job_description.txt')

# Determine paths
# __file__ is inside tailor_bot/
# os.path.dirname(__file__) is .../tailor_bot
# os.path.dirname(...) is the workspace root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_SOURCE_DIR = os.path.join(ROOT_DIR, 'base')

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def clean_llm_response(response):
    """
    Cleans the response from the LLM to ensure it's valid LaTeX.
    Removes markdown code blocks if present.
    """
    if response.startswith("```latex"):
        response = response[8:]
    elif response.startswith("```tex"):
        response = response[6:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()

def process_directory(client, target_base_dir, directory_name, jd_content):
    dir_path = os.path.join(target_base_dir, directory_name)
    if not os.path.exists(dir_path):
        print(f"Directory not found: {dir_path}")
        return

    print(f"\n--- Processing directory: {directory_name} ---")
    
    # List all .tex files
    for filename in os.listdir(dir_path):
        if filename.endswith(".tex"):
            base_name = filename[:-4]
            tex_path = os.path.join(dir_path, filename)
            txt_path = os.path.join(dir_path, base_name + ".txt")

            # Check if corresponding .txt master data file exists
            if os.path.exists(txt_path):
                print(f"Found pair: {filename} + {base_name}.txt")
                
                master_data = read_file(txt_path)
                current_tex = read_file(tex_path)

                if not master_data or not master_data.strip():
                    print(f"  Skipping {base_name}: Master data (.txt) is empty.")
                    continue

                print(f"  Tailoring {base_name}...")
                
                # Prepare Prompt
                prompt = TAILOR_PROMPT.format(
                    jd_content=jd_content,
                    txt_content=master_data,
                    tex_content=current_tex
                )

                # Call LLM
                new_content = client.generate_tailored_content(prompt)

                if new_content:
                    cleaned_content = clean_llm_response(new_content)
                    
                    # Backup original (optional in new folder, but good for reference)
                    write_file(tex_path + ".bak", current_tex)
                    
                    # Write new content
                    write_file(tex_path, cleaned_content)
                    print(f"  Success! Updated {filename}")
                else:
                    print(f"  Failed to generate content for {base_name}")
            else:
                # print(f"Skipping {filename}: No corresponding .txt file found.")
                pass

def create_output_folder(folder_name_prefix):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    folder_name = f"{folder_name_prefix}_{date_str}"
    target_path = os.path.join(ROOT_DIR, folder_name)
    return target_path

def main():
    print("Starting Resume Tailor Bot...")

    # 1. Get folder name from user
    if len(sys.argv) > 1:
        folder_prefix = sys.argv[1]
    else:
        folder_prefix = input("Enter the output folder name prefix (e.g. 'Google_SDE'): ").strip()
        if not folder_prefix:
            folder_prefix = "Tailored_Resume"

    # 2. Read Job Description
    jd_content = read_file(JD_FILE)
    if not jd_content or not jd_content.strip():
        print(f"Error: Job Description file is empty or missing at {JD_FILE}")
        print("Please paste the Job Description into that file and try again.")
        return

    # 3. Create Output Directory and Copy Base
    target_dir = create_output_folder(folder_prefix)
    
    print(f"Creating output directory: {target_dir}")
    try:
        if os.path.exists(target_dir):
             print(f"Directory {target_dir} already exists. Cleaning it up...")
             shutil.rmtree(target_dir)
        
        shutil.copytree(BASE_SOURCE_DIR, target_dir)
        print(f"Copied base template to {target_dir}")
    except Exception as e:
        print(f"Error copying base directory: {e}")
        return

    # 4. Initialize LLM Client
    try:
        client = LLMClient()
    except Exception as e:
        print(f"Error initializing LLM Client: {e}")
        return

    # 5. Process Directories in the NEW location
    for directory in DIRS_TO_PROCESS:
        process_directory(client, target_dir, directory, jd_content)

    print("\n--------------------------------------------------")
    print(f"Done! Tailored resume is in: {target_dir}")
    
    print("Compiling PDF...")
    compile_script = os.path.join(target_dir, 'compile.sh')
    
    # Ensure it's executable
    if os.path.exists(compile_script):
        os.chmod(compile_script, 0o755)
        
        # Run it
        try:
            subprocess.run(['./compile.sh'], cwd=target_dir, check=True)
            print(f"PDF compiled successfully! Check {os.path.join(target_dir, 'out', 'main.pdf')}")
        except subprocess.CalledProcessError as e:
            print(f"Error compiling PDF: {e}")
        except Exception as e:
            print(f"An error occurred during compilation: {e}")
    else:
        print("compile.sh not found in the target directory. Skipping compilation.")

    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
