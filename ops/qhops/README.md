# qhops portable

`qhops` is an external Windows helper for operating a Qwen Harness repository
without hard-coding a repository path into the tool.

## Install

Keep these files together in any permanent folder, for example:

    D:\qh-tools\
      qh_ops.py
      qhops.cmd
      install_qhops_path.cmd

Run once:

    D:\qh-tools\install_qhops_path.cmd

Open a new CMD window.

## First-time repository setup

    qhops init D:\qwen-harness-test

The selected repository is stored in:

    %USERPROFILE%\.qhops\config.json

## Normal use

    qhops status
    qhops verify
    qhops commit-impl
    qhops finish

## Repository selection

Priority is:

1. `qhops --repo <path> ...`
2. Current directory if it is inside a Qwen Harness repository
3. `QH_REPO` environment variable
4. Default repository saved by `qhops init`

Examples:

    qhops --repo D:\another-harness status

or:

    set QH_REPO=D:\another-harness
    qhops status
