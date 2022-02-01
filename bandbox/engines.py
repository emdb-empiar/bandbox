"""
Engines perform analyses on the tree. They are all run asynchronously for performance.

quick wins
- detect redundant dirs [S2.a]
- detect obvious folders e.g tiff/*.tif* [S2.b]
- detect system information [S2.c]
- detect excessive files per directory [S2.c]
- detect directories with mixed files [S3.a]
- detect cryptic names (against a dictionary) [N1]
- detect dates in names [N1.b]
- detect accessions e.g. 'EMPIAR' [N1.c]
- detect mixed case in names [N2.a]
- detect periods in names [N2.a]
- detect odd characters in names [N2.b]
- detect long names [N2.d]
- detect inconsistent names [N3.a]
- detect external references e.g. 'figure' [N3.c]
- detect words to avoid e.g. 'files', 'data' [N3.c]
- detect missing padding [N3.e]
- detect embedded paths (needs file format library) [N3.f]
- detect unknown extensions [M1.a]
- detect proprietary extensions [M1.b]
- detect presence of documentation e.g. README [M2.a]
- detect presence of checksums [M3]
- detect hard links
- detect symbolic links
- detect broken symbolic links
"""


async def s2_detect_redundant_directory(tree, lock, args):
    """Detect the presence of redundant directories

    A directory is redundant if:
    - it is empty
    - it is non-empty but is the only child of a parent folder
    """
    # empty folders
    empty_folders = tree.find_empty_directories(include_root=args.include_root)
    with lock:
        print(f"S2 - redundant directories...", end=" ")
        if empty_folders:
            print(f"fail [{len(empty_folders)} directories]")
            for folder in empty_folders:
                print(f"  * {folder}")
        else:
            print(f"ok")


async def s2_detect_obvious_folders(tree, lock, args):
    """Detect obvious folders"""
    obvious_folders = tree.find_obvious_folders(include_root=args.include_root)
    with lock:
        print(f"S2 - obvious directory names...", end=" ")
        if obvious_folders:
            print(f"fail [{len(obvious_folders)} directories]")
            for folder in obvious_folders:
                print(f"  * {folder}")
        else:
            print(f"ok")


async def s2_detect_system_information(tree, lock, args):
    """Detect system information"""


async def s2_detect_excessive_files_per_directory(tree, lock, args):
    """Detect excessive files per directory"""


# async def _detect_(tree, args):
#     """Detect"""

async def n2_detect_long_names(tree, lock, args):
    """Detect entities with very long names"""
    # print(f"info: working on {tree} with {args}...")


async def s2_detect_redundant_dirs(tree, lock, args):
    """Detect redundant directories"""
    # print(f"info: working on {tree} with {args}...")
