#!/usr/bin/env python3
"""
git_commit.py — APFS-safe git commit helper

Works around SIGBUS / "Resource deadlock avoided" errors that occur when
git tries to mmap index/object files on an APFS volume mounted into a
Linux VM.  All new objects are written to a temp directory on /tmp, then
copied back to .git/objects/.

Usage:
  python3 git_commit.py "commit message"                    # commit all untracked + modified
  python3 git_commit.py "commit message" file1 file2 ...    # commit specific files
  python3 git_commit.py "commit message" --tag TagName       # commit and tag
  python3 git_commit.py --tag-only TagName                  # tag HEAD without committing
  python3 git_commit.py --status                            # show what would be committed

The script:
  1. Reads the current HEAD tree via cat-file (read-only, works on APFS)
  2. Hashes new/changed file blobs with hash-object
  3. Builds new tree objects in pure Python (hashlib + zlib)
  4. Creates the commit with commit-tree
  5. Copies new objects back to .git/objects/
  6. Updates .git/refs/heads/<branch>
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path


# ── Globals ────────────────────────────────────────────────────────────

REPO = None          # repo root (set in main)
ALT_OBJ = None       # temp object directory on /tmp
ENV = None           # env dict with GIT_OBJECT_DIRECTORY

CO_AUTHOR = "Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"


# ── Low-level git helpers ──────────────────────────────────────────────

def git(*args, **kwargs):
    """Run a git command, return stdout. Uses ALT_OBJ env if set."""
    env = ENV or dict(os.environ)
    try:
        return subprocess.check_output(
            ['git'] + list(args), env=env, cwd=REPO,
            stderr=subprocess.PIPE, timeout=10
        ).decode().strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git {' '.join(args)} failed: {e.stderr.decode().strip()}")


def write_git_object(content_bytes, obj_type='tree'):
    """Write a git object in pure Python to ALT_OBJ. Returns hex SHA."""
    header = f'{obj_type} {len(content_bytes)}\0'.encode()
    full = header + content_bytes
    sha = hashlib.sha1(full).hexdigest()
    path = os.path.join(ALT_OBJ, sha[:2], sha[2:])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(zlib.compress(full))
    return sha


def make_tree_bytes(entries):
    """Build raw git tree content from list of (mode, name, sha_hex)."""
    # Git sorts tree entries: blobs by name, trees by name + '/'
    def sort_key(e):
        mode, name, _ = e
        return name + '/' if mode == '40000' else name
    buf = b''
    for mode, name, sha_hex in sorted(entries, key=sort_key):
        buf += f'{mode} {name}\0'.encode()
        buf += bytes.fromhex(sha_hex)
    return buf


# ── Tree manipulation ──────────────────────────────────────────────────

def get_tree_entries(tree_hash):
    """Read tree entries via cat-file (read-only, APFS-safe)."""
    out = git('cat-file', '-p', tree_hash)
    entries = []
    for line in out.split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        meta = parts[0].split()
        entries.append((meta[0], parts[1], meta[2]))  # mode, name, hash
    return entries


def find_entry(tree_hash, name):
    """Find a single entry in a tree by name. Returns (mode, hash) or None."""
    for mode, n, h in get_tree_entries(tree_hash):
        if n == name:
            return mode, h
    return None


def update_tree(tree_hash, updates):
    """
    Apply updates to a tree and return the new tree hash.
    updates: dict of {name: (mode, hash)} — set to None to delete.
    """
    entries = get_tree_entries(tree_hash)
    new_entries = []
    updated_names = set()

    for mode, name, h in entries:
        if name in updates:
            updated_names.add(name)
            if updates[name] is not None:
                new_mode, new_hash = updates[name]
                new_entries.append((new_mode, name, new_hash))
            # else: deleted (skip)
        else:
            new_entries.append((mode, name, h))

    # Add new entries that weren't replacements
    for name, val in updates.items():
        if name not in updated_names and val is not None:
            new_mode, new_hash = val
            new_entries.append((new_mode, name, new_hash))

    return write_git_object(make_tree_bytes(new_entries))


def set_nested_blob(root_tree, path_parts, blob_hash, file_mode='100644'):
    """
    Set a blob at a nested path inside a tree, rebuilding intermediate
    trees bottom-up. Returns the new root tree hash.
    """
    if len(path_parts) == 1:
        return update_tree(root_tree, {path_parts[0]: (file_mode, blob_hash)})

    dir_name = path_parts[0]
    rest = path_parts[1:]

    entry = find_entry(root_tree, dir_name)
    if entry:
        _, subtree_hash = entry
    else:
        # Create empty tree for new directory
        subtree_hash = write_git_object(b'')

    new_subtree = set_nested_blob(subtree_hash, rest, blob_hash, file_mode)
    return update_tree(root_tree, {dir_name: ('40000', new_subtree)})


# ── High-level operations ─────────────────────────────────────────────

def get_head_info():
    """Return (branch_name, commit_hash, tree_hash)."""
    head_ref = git('symbolic-ref', 'HEAD')  # e.g. refs/heads/main
    branch = head_ref.split('/')[-1]
    commit = git('rev-parse', 'HEAD')
    commit_data = git('cat-file', '-p', commit)
    tree = None
    for line in commit_data.split('\n'):
        if line.startswith('tree '):
            tree = line.split()[1]
            break
    return branch, commit, tree


def find_changed_files(specific_files=None):
    """
    Find files to commit. Returns list of relative paths.
    If specific_files given, use those. Otherwise find all untracked + modified.
    """
    if specific_files:
        # Verify they exist
        result = []
        for f in specific_files:
            p = os.path.join(REPO, f)
            if os.path.exists(p):
                result.append(f)
            else:
                print(f"  Warning: {f} not found, skipping")
        return result

    # Get untracked files
    untracked = []
    try:
        out = git('ls-files', '--others', '--exclude-standard')
        if out:
            untracked = out.split('\n')
    except:
        pass

    # Get modified (tracked) files
    modified = []
    try:
        out = git('diff', '--name-only', 'HEAD')
        if out:
            modified = out.split('\n')
    except:
        pass

    # Also check staged files (in case user ran git add)
    staged = []
    try:
        out = git('diff', '--cached', '--name-only')
        if out:
            staged = out.split('\n')
    except:
        pass

    all_files = list(set(untracked + modified + staged))
    # Filter out anything in .git/
    all_files = [f for f in all_files if f and not f.startswith('.git/')]
    return sorted(all_files)


def do_commit(message, files, tag=None):
    """Perform the commit using pure-Python object creation."""
    branch, head_commit, head_tree = get_head_info()
    print(f"  Branch: {branch}")
    print(f"  HEAD:   {head_commit[:12]}")
    print(f"  Files:  {len(files)}")

    if not files:
        print("\n  Nothing to commit.")
        return None

    # Hash all file blobs and build new tree
    current_tree = head_tree
    for filepath in files:
        abs_path = os.path.join(REPO, filepath)
        if not os.path.exists(abs_path):
            print(f"  Skip (deleted): {filepath}")
            continue

        blob_hash = git('hash-object', '-w', abs_path)
        path_parts = filepath.split('/')
        current_tree = set_nested_blob(current_tree, path_parts, blob_hash)
        print(f"  + {filepath}")

    if current_tree == head_tree:
        print("\n  No tree changes detected.")
        return None

    # Append co-author if not already in message
    if CO_AUTHOR not in message:
        message = message.rstrip() + f"\n\n{CO_AUTHOR}"

    # Create commit
    commit_hash = git('commit-tree', current_tree, '-p', head_commit, '-m', message)
    print(f"\n  Commit: {commit_hash[:12]}")

    # Copy new objects back to .git/objects/
    copied = 0
    git_objects = os.path.join(REPO, '.git', 'objects')
    for direntry in os.scandir(ALT_OBJ):
        if direntry.is_dir() and len(direntry.name) == 2 and direntry.name not in ('in', 'pa'):
            dest_dir = os.path.join(git_objects, direntry.name)
            os.makedirs(dest_dir, exist_ok=True)
            for obj_file in os.scandir(direntry.path):
                if obj_file.is_file():
                    dest = os.path.join(dest_dir, obj_file.name)
                    if not os.path.exists(dest):
                        shutil.copy2(obj_file.path, dest)
                        copied += 1

    # Update branch ref
    ref_path = os.path.join(REPO, '.git', 'refs', 'heads', branch)
    with open(ref_path, 'w') as f:
        f.write(commit_hash + '\n')

    print(f"  Objects: {copied} new")

    # Tag if requested
    if tag:
        do_tag(tag, commit_hash)

    # Verify
    verify = git('log', '--oneline', '-3')
    print(f"\n  Log:\n    " + verify.replace('\n', '\n    '))

    return commit_hash


def do_tag(tag_name, commit_hash=None):
    """Create a lightweight tag."""
    if commit_hash is None:
        commit_hash = git('rev-parse', 'HEAD')

    tag_path = os.path.join(REPO, '.git', 'refs', 'tags', tag_name)
    with open(tag_path, 'w') as f:
        f.write(commit_hash + '\n')
    print(f"  Tag: {tag_name} -> {commit_hash[:12]}")


def do_status():
    """Show what would be committed."""
    files = find_changed_files()
    if not files:
        print("  Nothing to commit (working tree clean)")
        return

    print(f"  {len(files)} file(s) to commit:\n")
    for f in files:
        # Determine if new or modified
        try:
            git('cat-file', '-e', f'HEAD:{f}')
            status = 'modified'
        except:
            status = 'new file'
        print(f"    {status}: {f}")


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    global REPO, ALT_OBJ, ENV

    parser = argparse.ArgumentParser(
        description='APFS-safe git commit helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('message', nargs='?', help='Commit message')
    parser.add_argument('files', nargs='*', help='Specific files to commit (default: all changed)')
    parser.add_argument('--tag', help='Create a tag after committing')
    parser.add_argument('--tag-only', metavar='NAME', help='Tag HEAD without committing')
    parser.add_argument('--status', action='store_true', help='Show what would be committed')
    parser.add_argument('--repo', default='.', help='Repository path (default: current dir)')

    args = parser.parse_args()

    # Find repo root
    REPO = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(REPO, '.git')):
        # Try to find it
        check = REPO
        while check != '/':
            if os.path.isdir(os.path.join(check, '.git')):
                REPO = check
                break
            check = os.path.dirname(check)
        else:
            print("Error: not a git repository")
            sys.exit(1)

    os.chdir(REPO)

    # Set up temp object directory
    ALT_OBJ = tempfile.mkdtemp(prefix='git_alt_obj_')
    os.makedirs(os.path.join(ALT_OBJ, 'info'), exist_ok=True)
    with open(os.path.join(ALT_OBJ, 'info', 'alternates'), 'w') as f:
        f.write(os.path.join(REPO, '.git', 'objects') + '\n')
    ENV = dict(os.environ, GIT_OBJECT_DIRECTORY=ALT_OBJ)

    try:
        if args.status:
            print("\ngit_commit.py — status\n")
            do_status()

        elif args.tag_only:
            print(f"\ngit_commit.py — tagging HEAD\n")
            do_tag(args.tag_only)

        elif args.message:
            print(f"\ngit_commit.py — committing\n")
            files = find_changed_files(args.files if args.files else None)
            do_commit(args.message, files, tag=args.tag)

        else:
            parser.print_help()

    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(ALT_OBJ)
        except:
            pass

    print()


if __name__ == '__main__':
    main()
