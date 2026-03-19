# Imports 
import logging
import subprocess
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Functions

# Validate Syntax
def validate_syntax(code: str, file_name: str) -> tuple[bool, str, int]:
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(code)
    #logger.info(f"validate_syntax: file written")
    try:
        syntax_result = subprocess.run(
            ["gcc", "-Wall", "-fsyntax-only", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        warnings = len(re.findall(r"warning:", syntax_result.stderr))
        if syntax_result.returncode == 0:
            return True, "The code passes the syntax check.", warnings
        else:
            return False, f"Syntax errors detected:\n{syntax_result.stderr.strip()}", warnings
    except Exception as e:
        return False, f"Exception during syntax validation: {e}", 0
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

def validate_build(code: str, file_name: str, build_command: str) -> tuple[bool, str]:
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(code)
    #logger.info(f"validate_build: file written")
    build_parts = build_command.split()
    build_ok = False
    build_msg = ""

    try:
        build_result = subprocess.run(
            build_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if build_result.returncode == 0:
            build_ok = True
            build_msg = "The code passes the build check."
        else:
            build_msg = f"Build errors detected:\n{build_result.stderr.strip()}"
    except Exception as e:
        build_msg = f"Exception during build validation: {e}"
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
        for file in os.listdir('.'):
            if file.endswith('.o'):
                os.remove(file)
        if build_ok and "-o" in build_parts:
            out_index = build_parts.index("-o") + 1
            if out_index < len(build_parts):
                executable = build_parts[out_index]
                if os.path.exists(executable):
                    os.remove(executable)

    return build_ok, build_msg