# Resume Tailor Bot

This bot automatically updates your LaTeX resume files based on a Job Description using an LLM (OpenAI).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Key**:
    - Open `.env` file.
    - Paste your OpenAI API Key: `OPENAI_API_KEY=sk-...`

3.  **Prepare Data**:
    - Ensure your `experience/` and `projects/` folders have pairs of files:
        - `example.tex`: The LaTeX file (used as a template).
        - `example.txt`: The **Master Data** file containing ALL details, metrics, and bullet points for that role.
    - **Important**: The bot will skip any file where the `.txt` file is empty.

## Usage

1.  **Paste Job Description**:
    - Copy the JD text into `job_description.txt`.

2.  **Run the Bot**:
    ```bash
    python main.py
    ```

3.  **Compile Resume**:
    - Go back to the `base` directory and run:
    ```bash
    ./compile.sh
    ```

## How it works
- It reads the JD.
- It iterates through `experience` and `projects` folders.
- For every `.tex` file, it looks for a matching `.txt` file.
- It sends the JD, the Master Data (.txt), and the current Layout (.tex) to the LLM.
- It overwrites the `.tex` file with the tailored version.
- It saves a backup of the original `.tex` file as `.tex.bak`.
