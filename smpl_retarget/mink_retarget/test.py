#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
load_motion.py  --  读取 .npy / .npz 动作文件并打印主要字段
用法:
    python load_motion.py path/to/file.npy
    python load_motion.py path/to/file.npz
"""

import sys
from pathlib import Path
import numpy as np
import torch

def load_npy(path: Path):
    """
    兼容两种情况:
    1) torch.save 保存的张量 (torch.load 读取)
    2) numpy.save 保存的数组或字典 (np.load 读取, allow_pickle=True)
    """
    try:
        obj = torch.load(path, map_location="cpu")
        print("✔ 通过 torch.load 成功读取 (torch.save 格式)")
        return obj
    except Exception:
        # 若不是 torch 格式再尝试 numpy
        data = np.load(path, allow_pickle=True)
        if isinstance(data, np.ndarray) and data.dtype == object:
            data = data.item()          # 把 object-array 转回 dict
            print("✔ 通过 np.load 读取到 Python dict")
        else:
            print("✔ 通过 np.load 读取到 numpy 数组: shape =", data.shape)
        return data

def load_npz(path: Path):
    """
    np.load(..., allow_pickle=False) 直接返回 NpzFile, 类似字典
    """
    zfile = np.load(path, allow_pickle=False)
    print("✔ 成功读取 npz，包含数组键：", list(zfile.keys()))
    return zfile      # 使用时 zfile['poses'] / zfile['trans'] ...

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    fpath = Path(sys.argv[1])
    if not fpath.exists():
        print(f"文件不存在: {fpath}")
        sys.exit(1)

    if fpath.suffix == ".npy":
        obj = load_npy(fpath)
    elif fpath.suffix == ".npz":
        obj = load_npz(fpath)
    else:
        print("只支持 .npy / .npz")
        sys.exit(1)

    # ─── 示例: 若读取到的是 motion_data dict ──────────────────────────
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, np.ndarray):
                print(f"{k:20s}  →  ndarray  shape={v.shape}  dtype={v.dtype}")
            else:
                print(f"{k:20s}  →  {type(v)}")

    # 示例: 若是 SkeletonMotion（torch.save）可按属性访问
    if isinstance(obj, dict) and "dof_pos" in obj:
        q = obj["dof_pos"]
        print("第一帧关节角 (rad) →", q[0])

if __name__ == "__main__":
    main()
