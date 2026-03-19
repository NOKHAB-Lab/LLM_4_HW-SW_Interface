import subprocess
import xml.etree.ElementTree as ET
import tempfile
import os

def evaluate_code_quality_from_string(code_str: str) -> int:
    """
    Evaluates the quality of a C code string using cppcheck.
    Returns a score from 1 to 5 based on medium and high severity issues.
    Automatically deletes the temporary file after analysis.
    """

    tmp_path = None

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as tmp_file:
            tmp_file.write(code_str)
            tmp_path = tmp_file.name

        # Run cppcheck
        result = subprocess.run(
            ["cppcheck", "--enable=all", "--xml", "--xml-version=2", tmp_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True
        )

        # Parse XML from stderr
        root = ET.fromstring(result.stderr)

        severity_map = {
            "style": "low",
            "performance": "low",
            "portability": "low",
            "information": "low",
            "warning": "medium",
            "unusedFunction": "medium",
            "error": "high",
            "fatal": "high"
        }

        counts = {"low": 0, "medium": 0, "high": 0}

        for error in root.findall(".//error"):
            severity = error.attrib.get("severity", "unknown")
            level = severity_map.get(severity, "medium")
            counts[level] += 1

        medium = counts["medium"]
        high = counts["high"]

        # Scoring logic
        if high >= 3:
            return 1
        elif high == 2 or medium > 6:
            return 2
        elif high == 1 or medium > 3:
            return 3
        elif medium > 0:
            return 4
        else:
            return 5

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1

    finally:
        # Ensure the temp file is deleted
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as cleanup_error:
                print(f"⚠️ Failed to delete temp file: {tmp_path} ({cleanup_error})")
