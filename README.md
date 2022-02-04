# `bandbox`

`bandbox` is a CLI tool to quickly evaluate how organised your dataset is. You can use `bandbox` on any directory and it will recursively descend through to all subdirectories to assess whether the structure and names are easy to use. `bandbox` reads in a set of constants from Github gist, which it uses to assess your dataset. Once complete, `bandbox` displays various assessments and whether they are `ok` or `nok`, together with details about which paths from the specified directory have failed that assessment. The use may also display the directory tree using the `--show-tree` option as well as summarise the output using the `--summarise` option which may be modified using the `--summarise-size` option. 

Bear in mind that `bandbox` only makes suggestions on how to make your dataset more usable; you are in the best position to decide whether a `fail` is a real fail. It might help you discover unwanted files e.g. `log` files, temporary files such as `*.tif~`, operating system fluff like `.DS_Store` files on macOS etc.

## Viewing the tree

Use the `view` command to view the tree implied by the dataset. 

```shell
~$ bandbox view # to view the current directory
~$ bandbox view some_path
~$ bandbox view some_path --prefix some_path # will exclude 'some_path' from every path entry
~$ bandbox view some_path --hide-file-counts # only show file totals
```

> Some options are experimental and incomplete e.g. `--input-file`, which takes the output of Python's `glob.glob(path, recursive=True)` function saved as a string.

Here is an example based on the `test_data` directory in the git repository:

```shell
~$ bandbox view test_data
info: successfully retrieved up-to-date data...
└── test_data
        └── folder_with_multiple_folders
                └── folder5
                        └── [10 files: tif=10; ]
                └── folder2
                        └── [10 files: tif=10; ]
                └── folder3
                        └── [10 files: tif=10; ]
                └── folder4
                        └── [10 files: tif=10; ]
                └── folder1
                        └── [10 files: tif=10; ]
                └── folder6
                        └── [100 files: dog=100; ]
        └── folder_with_single_file
                └── folder
                        └── [1 file: txt=1; ]
        └── folder_with_date_name_files
                └── [12 files: txt=10; raw=2; ]
        └── folder_with_multiple_files
                └── folder
                        └── [11 files: txt=10; tif=1; ]
        └── folder_with_multiple_file_types
                └── folder
                        └── [20 files: txt=10; tif=10; ]
                        └── files
                        └── inner_folder
        └── empty_folder
                └── folder
        └── single_empty_folder
                └── folder
                        └── inner_folder
        └── folder_with_long_name_folders
                └── a folder with spaces in the name
                └── folder
                        └── [26 files: dog=1; txt=11; tif=10; jpg=2; onx=1; wrx=1; ]
                        └── files
                        └── inner_folder
                                └── another_very_long_name_that_we_are_still_wondering_ever_found_the_light_of_day
                └── a folder with & funny symbols in the ?? name
                └── a_folder_with_a_very_long_name_that_we_cannot_even_begin_to_comprehend
                └── a.folder.with.periods.in.the.name
```

## Analysing the tree

Use the `analyse` command to run the assessments on your dataset. Here is an example output using the `--summarise` and `--show-tree` options:

> In the results below, **N** indicates a _naming_ issue, **S** a _structural_ issue (the folder structure) and **M** are _miscellaneous_ issues (e.g. warnings about unknown file extensions). Scroll horizontally (Shift+Scroll) to see the number of issues in each category.

```shell
~$ bandbox analyse test_data --show-tree --summarise
info: successfully retrieved up-to-date data...
└── test_data
        └── folder_with_multiple_folders
                └── folder5
                        └── [10 files: tif=10; ]
                └── folder2
                        └── [10 files: tif=10; ]
                └── folder3
                        └── [10 files: tif=10; ]
                └── folder4
                        └── [10 files: tif=10; ]
                └── folder1
                        └── [10 files: tif=10; ]
                └── folder6
                        └── [100 files: dog=100; ]
        └── folder_with_single_file
                └── folder
                        └── [1 file: txt=1; ]
        └── folder_with_date_name_files
                └── [12 files: txt=10; raw=2; ]
        └── folder_with_multiple_files
                └── folder
                        └── [11 files: txt=10; tif=1; ]
        └── folder_with_multiple_file_types
                └── folder
                        └── [20 files: txt=10; tif=10; ]
                        └── files
                        └── inner_folder
        └── empty_folder
                └── folder
        └── single_empty_folder
                └── folder
                        └── inner_folder
        └── folder_with_long_name_folders
                └── a folder with spaces in the name
                └── folder
                        └── [26 files: dog=1; txt=11; tif=10; jpg=2; onx=1; wrx=1; ]
                        └── files
                        └── inner_folder
                                └── another_very_long_name_that_we_are_still_wondering_ever_found_the_light_of_day
                └── a folder with & funny symbols in the ?? name
                └── a_folder_with_a_very_long_name_that_we_cannot_even_begin_to_comprehend
                └── a.folder.with.periods.in.the.name
 
M1 - unknown file extensions...                                                                       [103 directories] nok
  * test_data/folder_with_multiple_folders/folder6/file2.dog
  * test_data/folder_with_multiple_folders/folder6/file30.dog
  * test_data/folder_with_multiple_folders/folder6/file24.dog
  * test_data/folder_with_multiple_folders/folder6/file18.dog
  * test_data/folder_with_multiple_folders/folder6/file19.dog
  * [+98 others (remove --summarise option to view the full list)]

N1 - accessions in names...                                                                             [1 directories] nok
  * test_data/folder_with_multiple_files/folder/file-EMPIAR-someting.tif

N1 - entities with dates in names...                                                                   [10 directories] nok
  * test_data/folder_with_date_name_files/prefix-2000-12-31-suffix.txt
  * test_data/folder_with_date_name_files/prefix-001231-suffix.txt
  * test_data/folder_with_date_name_files/prefix-20001231-suffix.txt
  * test_data/folder_with_date_name_files/prefix-12312000-suffix.txt
  * test_data/folder_with_date_name_files/prefix-31-December-2000-suffix.txt
  * [+5 others (remove --summarise option to view the full list)]

N2 - excessive periods in names...                                                                      [2 directories] nok
  * test_data/folder_with_long_name_folders/folder/a.file.with.many.periods.txt
  * test_data/folder_with_long_name_folders/a.folder.with.periods.in.the.name

N2 - long names (>20 chars)...                                                                         [11 directories] nok
  * test_data/folder_with_multiple_folders
  * test_data/folder_with_single_file
  * test_data/folder_with_date_name_files
  * test_data/folder_with_multiple_files
  * test_data/folder_with_multiple_file_types
  * [+6 others (remove --summarise option to view the full list)]

N2 - mixed case in names...                                                                             [5 directories] nok
  * test_data/folder_with_date_name_files/prefix-31-Dec-2000-suffix.txt
  * test_data/folder_with_date_name_files/prefix-Dec-31-2000-suffix.txt
  * test_data/folder_with_date_name_files/prefix-31:December:2000-suffix.txt
  * test_data/folder_with_date_name_files/prefix-31-December-2000-suffix.txt
  * test_data/folder_with_multiple_files/folder/file-EMPIAR-someting.tif

N2 - odd characters in names...                                                                         [2 directories] nok
  * test_data/folder_with_long_name_folders/a folder with spaces in the name
  * test_data/folder_with_long_name_folders/a folder with & funny symbols in the ?? name

N3 - external references in names...                                                                    [2 directories] nok
  * test_data/folder_with_long_name_folders/folder/supplementary-figure3a.jpg
  * test_data/folder_with_long_name_folders/folder/figure5.jpg

S2 - excessives (>5) files per directory...                                                            [10 directories] nok
  * test_data/folder_with_multiple_folders/folder5/
  * test_data/folder_with_multiple_folders/folder2/
  * test_data/folder_with_multiple_folders/folder3/
  * test_data/folder_with_multiple_folders/folder4/
  * test_data/folder_with_multiple_folders/folder1/
  * [+5 others (remove --summarise option to view the full list)]

S2 - obvious directory names...                                                                        [11 directories] nok
  * test_data/folder_with_single_file/folder
  * test_data/folder_with_multiple_files/folder
  * test_data/folder_with_multiple_file_types/folder
  * test_data/folder_with_multiple_file_types/folder/files
  * test_data/folder_with_multiple_file_types/folder/inner_folder
  * [+6 others (remove --summarise option to view the full list)]

S2 - redundant directories...                                                                          [16 directories] nok
  * test_data/folder_with_multiple_files
  * test_data/folder_with_multiple_file_types
  * test_data/folder_with_multiple_file_types/folder/files
  * test_data/folder_with_multiple_file_types/folder/inner_folder
  * test_data/empty_folder
  * [+11 others (remove --summarise option to view the full list)]

S3 - directories with mixed files...                                                                    [4 directories] nok
  * test_data/folder_with_date_name_files/
  * test_data/folder_with_multiple_files/folder/
  * test_data/folder_with_multiple_file_types/folder/
  * test_data/folder_with_long_name_folders/folder/

```

## Updating the settings
When analysing a tree, `bandbox` reads data from https://gist.github.com/paulkorir/5b71f57f7a29391f130e53c24a2db3fb/raw/bandbox.json. This data is public and subject to revision. If you would like to expand a particular criterion for analysis please fork the gist, for the repo, test then send a PR for it to be included. Eventually, this will be simplified by using a CLI option. 

### Current settings

```json
{
  "file_formats": "jpg|jpeg|mrc|mrcs|tif|tiff|dm4|txt|box|cfg|fixed|st|rec|map|bak|eer|bz2|gz|zip|xml|am|star|raw|dat",
  "obvious_files": "images|directory",
  "max_files": 2000,
  "max_name_length": 50,
  "date_infix_chars": "=",
  "month_chars": "",
  "date_re": [],
  "accession_names": "EMDB|EMPIAR|BIOSTUDIES",
  "odd_chars": "&?! %^*@£$#(){}",
  "max_periods_in_name": 1,
  "external_refs": "figure|supplementary"
}
```
