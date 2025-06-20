from __future__ import annotations

import os
from pathlib import Path


def is_safe_fullpath(
    candidate: str | os.PathLike,
    *,
    root: str | os.PathLike | None = None
) -> bool:
    """
    実在の有無を問わず「安全な絶対パス」かどうか判定する。

    安全の意味:
    1. 絶対パスである
    2. ".." によるパストラバーサルが除去された結果でも絶対パス
    3. （root を指定した場合）その配下に収まる

    Parameters
    ----------
    candidate : str | PathLike
        判定対象のパス文字列。
    root : str | PathLike | None, default=None
        ここで指定したディレクトリ配下に収まっているかチェックする。
        None ならこのチェックは行わない。

    Returns
    -------
    bool
        条件を満たせば True、そうでなければ False。
    """
    # 基本チェック
    try:
        cand_str = os.fspath(candidate)
    except (TypeError, ValueError):
        return False
    if not cand_str or "\x00" in cand_str:
        return False

    p = Path(cand_str)

    # ① 絶対パスでなければ NG
    if not p.is_absolute():
        return False

    # ② 正規化して ../ を除去（存在しなくても strict=False で OK）
    normalized = p.resolve(strict=False)

    # resolve しても '..' が残っていれば NG
    if ".." in normalized.parts:
        return False

    # ③ root 配下チェック（オプション）
    if root is not None:
        root_path = Path(root).resolve(strict=False)
        try:
            normalized.relative_to(root_path)
        except ValueError:
            return False

    return True