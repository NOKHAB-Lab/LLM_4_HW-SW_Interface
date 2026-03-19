import re

def strip_c_comments(code: str) -> str:
    """Remove C-style (// and /* */) comments."""
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code

# ------------------------------------------
# Individual C++ checks — now return list of matched patterns
# ------------------------------------------

def has_cpp_headers(code: str) -> list[str]:
    patterns = [
        r'#include\s*<iostream>',
        r'#include\s*<string>',
        r'#include\s*<sstream>',
        r'#include\s*<vector>',
        r'#include\s*<map>',
        r'#include\s*<set>',
        r'#include\s*<list>',
        r'#include\s*<deque>',
        r'#include\s*<algorithm>',
        r'#include\s*<functional>',
        r'#include\s*<stdexcept>',
    ]
    return [p for p in patterns if re.search(p, code)]

def has_cpp_namespaces(code: str) -> list[str]:
    patterns = [
        r'\bnamespace\s+\w+',
        r'\busing\s+namespace\s+std\b',
    ]
    return [p for p in patterns if re.search(p, code)]

def has_cpp_keywords(code: str) -> list[str]:
    patterns = [
        r'\bclass\s+\w+',
        r'\btemplate\s*<',
        r'\bpublic\s*:', r'\bprivate\s*:', r'\bprotected\s*:',
        r'\btry\b', r'\bcatch\s*\(',
        r'\bexplicit\b',
        r'\boverride\b',
        r'\bconstexpr\b',
        r'\bnoexcept\b',
        r'\bnullptr\b',
    ]
    return [p for p in patterns if re.search(p, code)]

def has_cpp_syntax(code: str) -> list[str]:
    patterns = [
        r'\bstd::\w+',
        r'\bnew\s+\w+',
        r'\bdelete\s+\w+',
        r'\bcout\s*<<', r'\bcin\s*>>', r'\bendl\b',
    ]
    return [p for p in patterns if re.search(p, code)]


def has_cpp_memory_utils(code: str) -> list[str]:
    patterns = [
        r'\bstd::unique_ptr\b',
        r'\bstd::shared_ptr\b',
        r'\bstd::make_shared\b',
        r'\bstd::make_unique\b',
    ]
    return [p for p in patterns if re.search(p, code)]

# ------------------------------------------
# Master function
# ------------------------------------------

def is_valid_c_code_with_no_cpp_indicator(code: str) -> tuple[bool, str]:
    """
    Returns (is_valid, matched_patterns_csv)
    is_valid = False if any C++ constructs are detected.
    matched_patterns_csv = comma-separated string of matched regex patterns.
    """
    code = strip_c_comments(code)

    cpp_checks = [
        has_cpp_headers,
        has_cpp_namespaces,
        has_cpp_keywords,
        has_cpp_syntax,
        has_cpp_memory_utils,
    ]

    matched_patterns = []

    for check in cpp_checks:
        matched_patterns.extend(check(code))

    matched_csv = ", ".join(matched_patterns)
    return (len(matched_patterns) == 0), matched_csv
