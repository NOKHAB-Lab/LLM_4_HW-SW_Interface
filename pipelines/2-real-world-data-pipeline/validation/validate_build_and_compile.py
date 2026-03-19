import subprocess
import os
import copy


def validate_build_and_compile(entry: dict) -> tuple[bool, str]:
    """
    Validates syntax and build of a C code entry without modifying the original object.
    Returns:
        (bool): True if both syntax and build pass, else False.
        (str): Detailed message including pass/fail status and errors.
    """
    entry_copy = copy.deepcopy(entry)
    file_name = entry_copy.get("file-name")
    code = entry_copy.get("output", "")
    build_cmd = entry_copy.get("build-command", "")

    if not file_name or not code or not build_cmd:
        return False, "The generated should always contain the file-name, output, and the build-command."

    # Write code to file
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
            syntax_msg = "The code should pass the syntax check."
        else:
            syntax_msg = f"The code should pass the syntax check using the gcc -fsyntax-only command. It should be syntatically valid. It should not have syntax errors like: \n{syntax_result.stderr.strip()}"
    except Exception as e:
        syntax_msg = f"The code should not have syntax errors: {e}"

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
            build_msg = "The code should pass the build check against the build-command."
        else:
            build_msg = f"The code should pass the build check against the build-command. It should be buildable while avoiding build errors like:\n{build_result.stderr.strip()}"
    except Exception as e:
        build_msg = f"The code should not have build errors: {e}"

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
    except Exception as e:
        return False, f"{syntax_msg}\n{build_msg}"

    overall_success = syntax_ok and build_ok
    return overall_success, f"The code should be robust, {syntax_msg}\n{build_msg}"
