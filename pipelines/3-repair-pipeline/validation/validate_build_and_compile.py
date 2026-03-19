import subprocess
import os
import copy

def validate_build_and_compile(entry: dict) -> tuple[dict, bool, str]:
    """
    Validates syntax and build of a C code entry without modifying the original object.
    Returns:
        updated_entry (dict): Copy of the original entry with updated fields
        success (bool): True if both syntax and build pass, else False
        message (str): Summary of validation results
    """
    entry_copy = copy.deepcopy(entry)
    file_name = entry_copy.get("file-name")
    code = entry_copy.get("output", "")
    build_cmd = entry_copy.get("build-command", "")

    if not file_name or not code or not build_cmd:
        return entry_copy, False, "❌ 'file-name', 'output', or 'build-command' is missing."

    # Write code to temp file
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(code)

    syntax_ok = False
    build_ok = False
    syntax_msg = ""
    build_msg = ""

    # ---- SYNTAX CHECK ----
    try:
        syntax_result = subprocess.run(
            ["gcc", "-fsyntax-only", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if syntax_result.returncode == 0:
            syntax_ok = True
            entry_copy["syntax_status"] = "success"
            entry_copy.pop("syntax_error", None)
            syntax_msg = "✅ Syntax check passed."
        else:
            entry_copy["syntax_status"] = "fail"
            entry_copy["syntax_error"] = syntax_result.stderr.strip()
            syntax_msg = "❌ Syntax check failed using `gcc -fsyntax-only`."
    except Exception as e:
        entry_copy["syntax_status"] = "fail"
        entry_copy["syntax_error"] = str(e)
        syntax_msg = f"❌ Syntax check failed with exception: {e}"

    # ---- BUILD CHECK ----
    try:
        build_parts = build_cmd.split()
        build_result = subprocess.run(
            build_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if build_result.returncode == 0:
            build_ok = True
            entry_copy["build_status"] = "success"
            entry_copy.pop("build_error", None)
            build_msg = "✅ Build check passed."
        else:
            entry_copy["build_status"] = "fail"
            entry_copy["build_error"] = build_result.stderr.strip()
            build_msg = "❌ Build check failed using build command."
    except Exception as e:
        entry_copy["build_status"] = "fail"
        entry_copy["build_error"] = str(e)
        build_msg = f"❌ Build failed with exception: {e}"

    # ---- CLEANUP ----
    try:
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
    except Exception:
        pass  # silently ignore cleanup errors

    overall_success = syntax_ok and build_ok
    return entry_copy, overall_success, f"Summary: {syntax_msg}\n{build_msg}"
