"""
Engines perform analyses on the tree. They are all run concurrently for performance.

quick wins
- [DONE] detect redundant dirs [S2.a]
- [DONE] detect obvious folders e.g tiff/*.tif* [S2.b]
- [DONE] detect excessive files per directory [S2.c]
- [DONE] detect directories with mixed files [S3.a]
- detect cryptic names (against a dictionary) [N1]
- [DONE] detect dates in names [N1.b]
- [DONE] detect accessions e.g. 'EMPIAR' [N1.c]
- [DONE] detect mixed case in names [N2.a]
- detect periods in names [N2.a]
- [DONE] detect odd characters in names [N2.b]
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

import shutil

import styled

import bandbox

# import threading # doesn't seem to be necessary

width, height = shutil.get_terminal_size((80, 60))
RIGHT_COL_WIDTH = 40
LEFT_COL_WIDTH = width - RIGHT_COL_WIDTH - 1


async def _report(dirs: list, rule_text: str, fail_text: str = '') -> None:
    """Reporting function"""
    # lock = threading.Lock()
    # with lock:
    print(styled.Styled(f"[[ '{rule_text.ljust(LEFT_COL_WIDTH)}'|bold ]]"), end=" ")
    if dirs:
        if fail_text:
            print(styled.Styled(f"[[ '{fail_text.rjust(RIGHT_COL_WIDTH)}'|fg-red:bold ]]"))
        else:
            fail_text = f"fail [{len(dirs)} directories]".rjust(RIGHT_COL_WIDTH)
            print(styled.Styled(f"[[ '{fail_text}'|fg-red:bold ]]"))
        for item in dirs:
            print(f"  * {item}")
    else:
        ok_text = "ok".rjust(RIGHT_COL_WIDTH)
        print(styled.Styled(f"[[ '{ok_text}'|fg-green:bold ]]"))
    print()


async def s2_detect_redundant_directories(tree, args):
    """Detect the presence of redundant directories

    A directory is redundant if:
    - it is empty
    - it is non-empty but is the only child of a parent folder
    """
    # empty folders
    empty_folders = tree.find_empty_directories(include_root=args.include_root)
    await _report(empty_folders, f"S2 - redundant directories...")


async def s2_detect_obvious_directories(tree, args):
    """Detect obvious folders"""
    obvious_folders = tree.find_obvious_directories(include_root=args.include_root)
    await _report(obvious_folders, f"S2 - obvious directory names...")


async def s2_detect_excessive_files_per_directory(tree, args):
    """Detect excessive files per directory"""
    excess_files = tree.find_excessive_files_per_directory()
    await _report(excess_files, f"S2 - excessives (>{bandbox.MAX_FILES}) files per directory...")


async def s3_detect_directories_with_mixed_files(tree, args):
    """Detect folders with mixed files"""
    mixed_files = tree.find_directories_with_mixed_files()
    await _report(mixed_files, f"S3 - directories with mixed files...")


async def n2_detect_long_names(tree, args):
    """Detect entities with very long names"""
    # print(f"info: working on {tree} with {args}...")
    dirs = tree.find_long_names()
    await _report(dirs, f"N2 - long names (>{bandbox.MAX_NAME_LENGTH} chars)...")


async def n1_detect_dates_in_names(tree, args):
    """Detect dates of various formats in names"""
    dirs = tree.find_with_date_names()
    await _report(dirs, f"N1 - entities with dates in names...")


async def n1_detect_accessions_in_names(tree, args):
    """Detect accessions in names"""
    dirs = tree.find_accessions_in_names()
    await _report(dirs, f"N1 - accessions in names...")


async def n2_detect_mixed_case(tree, args):
    """Detect mixed case"""
    dirs = tree.find_mixed_case()
    await _report(dirs, f"N2 - mixed case in names...")


async def n2_detect_odd_characets_in_names(tree, args):
    dirs = tree.find_odd_characters_in_names()
    await _report(dirs, f"N2 - odd characters in names...")


async def n2_detect_excessive_periods_in_names(tree, args):
    dirs = tree.find_excessive_periods_in_names()
    await _report(dirs, f"N2 - excessive periods in names...")
