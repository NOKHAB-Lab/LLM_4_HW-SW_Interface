import re
import shlex

def build_command_looks_cpp(build_cmd: str) -> bool:
    """
    Analyze the build command and return True if it shows C++ usage.
    This includes g++, .cpp files, and C++-specific libraries.
    """
    if not build_cmd:
        return False

    try:
        tokens = shlex.split(build_cmd)  # Safely split respecting quotes
    except ValueError:
        tokens = build_cmd.split()  # Fallback to naive split

    cpp_indicators = {
        "compilers": ["g++", "clang++"],
        "file_extensions": [".cpp", ".cc", ".cxx", ".hpp"],
        "cpp_flags": [
            "-lstdc++", "-lc++", "-lboost", "-lopencv", "-lopencv_core", "-lboost_system",
            "-stdlib=libc++"
        ],
        "pkg_patterns": [r"pkg-config\s+--cflags\s+--libs\s+opencv"]
    }

    for token in tokens:
        token_lower = token.lower()

        # Check compiler
        if token_lower in cpp_indicators["compilers"]:
            return True

        # Check file extensions
        if any(token_lower.endswith(ext) for ext in cpp_indicators["file_extensions"]):
            return True

        # Check explicit C++ link flags
        if token_lower in cpp_indicators["cpp_flags"]:
            return True

        # Catch pkg-config for opencv or similar C++ packages
        for pattern in cpp_indicators["pkg_patterns"]:
            if re.search(pattern, build_cmd, re.IGNORECASE):
                return True

    return False