from pathlib import Path

path = Path("tools/qh.py")
text = path.read_text(encoding="utf-8")
old = '''    relative_text = relative.as_posix()\n    _run_git(\n        str(repo_root),\n        ("cat-file", "-e", f"HEAD:{relative_text}"),\n    )\n    return relative_text\n'''
new = '''    relative_text = relative.as_posix()\n    if relative_text == "STATUS.md" or relative_text.startswith("tasks/"):\n        raise ValueError("Lifecycle-control files cannot be used as Evidence")\n\n    _run_git(\n        str(repo_root),\n        ("cat-file", "-e", f"HEAD:{relative_text}"),\n    )\n    return relative_text\n'''
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected exactly one evidence validation target, found {count}")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8", newline="\n")
print("hardened lifecycle Evidence validation")
