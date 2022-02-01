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


async def s2_detect_redundant_directory(tree, args):
    """Detect the presence of redundant directories"""

async def s2_detect_obvious_folders(tree, args):
    """Detect obvious folders"""

async def s2_detect_system_information(tree, args):
    """Detect system information"""

async def s2_detect_excessive_files_per_directory(tree, args):
    """Detect excessive files per directory"""

# async def _detect_(tree, args):
#     """Detect"""

async def n2_detect_long_names(tree, args):
    """Detect entities with very long names"""
    print(f"info: working on {tree} with {args}...")


async def s2_detect_redundant_dirs(tree, args):
    """Detect redundant directories"""
    print(f"info: working on {tree} with {args}...")
