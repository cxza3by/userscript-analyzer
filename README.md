# UserScript Analyzer CLI 😋🥭❤️

A Python command-line utility designed to automatically download, save, and analyze JavaScript UserScripts using advanced AI models via Hugging Face.

## Setup

1. Create virtual environment *(venv)* in the root directory:
   ```bash
   python -m venv venv
   source ./venv/bin/activate
   ```
2. Before running the script, ensure you have Python installed and install the required dependencies:
   ```bash
   pip install requests python-dotenv huggingface_hub
   ```
3. Create a `.env` file in the root directory of the project.
4. Add your Hugging Face API token to the file:
   ```env
   HF_TOKEN=your_token_here
   ```

## Usage

You can pass a specific file, a URL, or run the script without arguments to use the default file.

### Available Arguments

* `--url "LINK"` – Automatically downloads a script from a direct link (supports GreasyFork and GitHub blobs), saves it to the `scripts/` folder, and analyzes it.
* `--file "filename.js"` – Analyzes a specific JavaScript file already located inside the `scripts/` folder.
* **No arguments** – The script will look for `scripts/input_script.js`. If it doesn't exist, it will create a template file for you to paste your code into.

### Examples

**Analyze from a URL:**
```bash
python main.py --url "https://github.com/xxx/xxx/tree/main/some-script.js"
```

**Analyze an existing file:**
```bash
python main.py --file "yourscript.js"
```

**Run using default file:**
```bash
python main.py
```

## How It Works

1. **Download/Load:** The script fetches the JavaScript code via URL or loads it from the local `scripts/` directory.
2. **AI Analysis:** The code is sent to the `Qwen/Qwen2.5-Coder-32B-Instruct` model hosted on Hugging Face.
3. **Report Generation:** The resulting AI markdown report is saved both with a unique timestamp in the `reports/` folder (e.g., `reports/report_2026-08-21_11-00-00.md`) and duplicated into `answer.md` for quick access.
