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
- [DONE] detect periods in names [N2.a]
- [DONE] detect odd characters in names [N2.b]
- [DONE] detect long names [N2.d]
- detect inconsistent names [N3.a]
- [DONE] detect external references e.g. 'figure' [N3.c]
- [DONE] detect words to avoid e.g. 'files', 'data' [N3.c]
- detect missing padding [N3.e]
- detect embedded paths (needs file format library) [N3.f]
- [DONE] detect unknown extensions [M1.a]
- [DONE] detect proprietary extensions [M1.b]
- detect presence of documentation e.g. README [M2.a]
- detect presence of checksums [M3]
- detect hard links
- detect symbolic links
- detect broken symbolic links
"""

import shutil

import styled

import bandbox

width, height = shutil.get_terminal_size((80, 60))
RIGHT_COL_WIDTH = 40
LEFT_COL_WIDTH = width - RIGHT_COL_WIDTH - 1


async def _report(dirs: list, rule_text: str, fail_text: str = '', args=None) -> None:
    """Reporting function"""
    summarise = getattr(args, 'summarise', False)
    summarise_size = getattr(args, 'summarise_size', 5)
    print(styled.Styled(f"[[ '{rule_text.ljust(LEFT_COL_WIDTH)}'|bold ]]"), end=" ")
    if dirs:
        if fail_text:
            print(styled.Styled(f"[[ '{fail_text.rjust(RIGHT_COL_WIDTH)}'|fg-red:bold ]]"))
        else:
            fail_text = f"[{len(dirs)} directories] nok".rjust(RIGHT_COL_WIDTH)
            print(styled.Styled(f"[[ '{fail_text}'|fg-red:bold ]]"))
        if summarise and len(dirs) > summarise_size:
            dirs_ = dirs[:summarise_size]
        else:
            dirs_ = dirs
        for item in dirs_:
            print(f"  * {item}")
        if summarise and len(dirs) > summarise_size:
            print(f"  * [+{len(dirs) - summarise_size} others (remove --summarise option to view the full list)]")

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
    await _report(empty_folders, f"{'structure warning':<17} => - redundant directories...", args=args)


async def s2_detect_obvious_directories(tree, args):
    """Detect obvious folders"""
    obvious_folders = tree.find_obvious_directories(include_root=args.include_root)
    await _report(obvious_folders, f"{'structure warning':<17} => - obvious directory names...", args=args)


async def s2_detect_excessive_files_per_directory(tree, args):
    """Detect excessive files per directory"""
    excess_files = tree.find_excessive_files_per_directory()
    await _report(excess_files, f"{'structure warning':<17} => - excessives (>{args._configs.getint('bandbox', 'max_files')}) files per directory...", args=args)


async def s3_detect_directories_with_mixed_files(tree, args):
    """Detect folders with mixed files"""
    mixed_files = tree.find_directories_with_mixed_files()
    await _report(mixed_files, f"{'structure warning':<17} => - directories with mixed files...", args=args)


async def n2_detect_long_names(tree, args):
    """Detect entities with very long names"""
    # print(f"info: working on {tree} with {args}...")
    dirs = tree.find_long_names()
    await _report(dirs, f"{'name warning':<17} => - long names (>{args._configs.getint('bandbox', 'max_name_length')} chars)...", args=args)


async def n1_detect_dates_in_names(tree, args):
    """Detect dates of various formats in names"""
    dirs = tree.find_with_date_names()
    await _report(dirs, f"{'name warning':<17} => - entities with dates in names...", args=args)


async def n1_detect_accessions_in_names(tree, args):
    """Detect accessions in names"""
    dirs = tree.find_accessions_in_names()
    await _report(dirs, f"{'name warning':<17} => - accessions in names...", args=args)


async def n2_detect_mixed_case(tree, args):
    """Detect mixed case"""
    dirs = tree.find_mixed_case()
    await _report(dirs, f"{'name warning':<17} => - mixed case in names...", args=args)


async def n2_detect_odd_characets_in_names(tree, args):
    dirs = tree.find_odd_characters_in_names()
    await _report(dirs, f"{'name warning':<17} => - odd characters [one of '{args._configs.get('bandbox', 'odd_chars')}'] in names...", args=args)


async def n2_detect_excessive_periods_in_names(tree, args):
    dirs = tree.find_excessive_periods_in_names()
    await _report(dirs, f"{'name warning':<17} => - excessive periods in names...", args=args)


async def n3_detect_external_references_in_names(tree, args):
    dirs = tree.find_external_references_in_names()
    await _report(dirs, f"{'name warning':<17} => - external references in names...", args=args)


async def m1_detect_unknown_file_extensions(tree, args):
    dirs = tree.find_unknown_file_extensions()
    await _report(dirs, f"{'misc. warning':<17} => - unknown file extensions...", args=args)


async def n2_detect_non_ascii_characters_in_names(tree, args):
    dirs = tree.find_non_ascii_characters()
    await _report(dirs, f"{'name warning':<17} => - non-ascii characters in names...", args=args)
