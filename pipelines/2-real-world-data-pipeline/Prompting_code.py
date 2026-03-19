import os
import json
import glob
import time
import argparse
import requests
from datetime import datetime

class SimplePiProcessor:
    def __init__(self, api_keys=None):
        """Initialize with API keys and output file"""
        # API settings
        self.API_KEYS = api_keys or [
            "YOUR_GEMINI_API_KEY_1",  # Replace with your Gemini API key
            "YOUR_GEMINI_API_KEY_2",  # Optional: add more keys for rotation
            "YOUR_GEMINI_API_KEY_3"   # Optional: add more keys for rotation
        ]
        self.current_key_index = 0
        self.API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={}"
        
        # Storage for all processed files
        self.all_data = {}
        self.output_file = "raspberry_pi_data.json"
        
        # Load existing data if available
        self._load_existing_data()
        
    def _load_existing_data(self):
        """Load existing data from output file if it exists"""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    self.all_data = json.load(f)
                print(f"Loaded {len(self.all_data)} existing entries from {self.output_file}")
            except Exception as e:
                print(f"Error loading existing data: {e}")
                self.all_data = {}
    
    def _save_data(self):
        """Save all data to the output file"""
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.all_data, f, indent=2)
            print(f"Saved {len(self.all_data)} entries to {self.output_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _get_next_api_key(self):
        """Get the next API key in rotation"""
        key = self.API_KEYS[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.API_KEYS)
        return key
    
    def call_gemini_api(self, prompt):
        """Call the Gemini API with a prompt"""
        api_key = self._get_next_api_key()
        api_url = self.API_URL_TEMPLATE.format(api_key)
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
                "topP": 0.95
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"API error: Status {response.status_code}")
                return f"Error: API returned status {response.status_code}"
            
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "Error: Unexpected API response structure"
        except Exception as e:
            return f"Error calling API: {str(e)}"
    
    def is_raspberry_pi_code(self, code, filename):
        """Check if the code is for Raspberry Pi"""
        prompt = f"""
        Analyze this Python code and tell me if it is specifically designed for use with a Raspberry Pi.
        Answer with ONLY "YES" or "NO".
        
        Filename: {filename}
        
        Code:
        {code}
        """
        
        response = self.call_gemini_api(prompt)
        # Check if response contains YES (case insensitive)
        return "YES" in response.upper()
    
    def generate_prompt(self, code, filename):
        """Generate a detailed prompt describing what the code does"""
        prompt = f"""
        You are an expert Raspberry Pi developer. Analyze this Python code for a Raspberry Pi project
        and generate a detailed prompt that describes exactly what it does and what task it accomplishes.

        Your prompt should include:
        1. A clear title and description of the project's purpose
        2. Hardware requirements (sensors, pins, connections)
        3. Software dependencies 
        4. Explanation of how the code works
        5. Expected outputs and behavior

        Filename: {filename}

        Code:
        {code}
        """
        
        return self.call_gemini_api(prompt)
    
    def generate_improved_code(self, code, filename):
        """Generate an improved version of the code"""
        prompt = f"""
        You are an expert Raspberry Pi developer. Improve this Python code for a Raspberry Pi project.
        Maintain the same functionality but make improvements for:
        - Better code structure and organization
        - Better error handling
        - Better commenting and documentation
        - Better variable naming
        - Better performance
        
        Respond ONLY with the improved code, no explanations.
        
        Filename: {filename}
        
        Code:
        {code}
        """
        
        return self.call_gemini_api(prompt)
    
    def process_file(self, file_path):
        """Process a single Python file"""
        # Skip if already processed
        if file_path in self.all_data:
            print(f"Skipping already processed file: {file_path}")
            return False
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            if not code.strip():
                print(f"Empty code file: {file_path}")
                return False
            
            filename = os.path.basename(file_path)
            print(f"Processing {filename}...")
            
            # Check if it's a Raspberry Pi code
            is_pi_code = self.is_raspberry_pi_code(code, filename)
            
            if not is_pi_code:
                print(f"Not a Raspberry Pi code: {filename}")
                # Still store the result to avoid reprocessing
                self.all_data[file_path] = {
                    "filename": filename,
                    "is_raspberry_pi_code": False,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source_code": code
                }
                self._save_data()
                return False
            
            # Generate prompt
            print(f"Generating prompt for {filename}...")
            prompt = self.generate_prompt(code, filename)
            
            # Generate improved code
            print(f"Generating improved code for {filename}...")
            improved_code = self.generate_improved_code(code, filename)
            
            # Store all data
            self.all_data[file_path] = {
                "filename": filename,
                "is_raspberry_pi_code": True,
                "source_code": code,
                "prompt": prompt,
                "improved_code": improved_code,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save after each file
            self._save_data()
            
            print(f"Successfully processed {filename}")
            return True
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def process_directory(self, directory):
        """Process all Python files in a directory"""
        # Get all Python files
        python_files = glob.glob(os.path.join(directory, "**", "*.py"), recursive=True)
        print(f"Found {len(python_files)} Python files in {directory}")
        
        processed_count = 0
        for file_path in python_files:
            success = self.process_file(file_path)
            if success:
                processed_count += 1
            
            # Don't overwhelm the API
            time.sleep(1)
        
        print(f"Successfully processed {processed_count} files")
        return processed_count

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simple Raspberry Pi Code Processor')
    parser.add_argument('--input-dir', type=str, required=True, help='Input directory containing Python files')
    parser.add_argument('--api-keys', type=str, help='Comma-separated list of Gemini API keys')
    args = parser.parse_args()
    
    # Parse API keys if provided
    api_keys = None
    if args.api_keys:
        api_keys = [key.strip() for key in args.api_keys.split(',')]
    
    # Create processor and process the directory
    processor = SimplePiProcessor(api_keys=api_keys)
    processor.process_directory(args.input_dir)

if __name__ == "__main__":
    main()