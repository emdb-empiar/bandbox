"""
Engines perform analyses on the tree. They are all run asynchronously for performance.
"""


async def n2_detect_long_names(tree, args):
    """Detect entities with very long names"""
    print(f"info: working on {tree} with {args}...")


async def s2_detect_redundant_dirs(tree, args):
    """Detect redundant directories"""
    print(f"info: working on {tree} with {args}...")
