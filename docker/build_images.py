"""组装 Docker 构建上下文并构建镜像（构建工具，不属于平台 scripts）。

为什么需要组装：
平台通过目录链接引入仓外模块（app/<module>、web/src/features/<module>），
Docker 不会跟随指向构建上下文之外的软链接。这里把链接解引用成真实目录，
再让 Docker 用普通上下文构建，避免 named context、逐模块参数和 .dockerignore 里的模块名单。

用法（在仓库根执行）：
    uv run python docker/build_images.py all      # web + backend
    uv run python docker/build_images.py web
    uv run python docker/build_images.py backend

产物：
    docker/build/            临时完整项目；构建前重建，构建后可删

构建参数：
    --cn        使用国内镜像源（pip/uv: USTC，npm: npmmirror）
    ORANGE_APP_IMAGE / ORANGE_WEB_IMAGE   镜像名（缺省 dev）
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 仓库根与临时构建上下文
ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / 'docker' / 'build'

# web/ 下不进入上下文的依赖/产物/本地环境：镜像内会重新安装或生成
WEB_IGNORES = ('node_modules', 'dist', '.env', '.env.*', '*.tsbuildinfo', '.vite')
# app/ 下的 Python 缓存，避免把旧字节码带进镜像
BACKEND_IGNORES = ('__pycache__', '*.pyc', '*.pyo')

# 后端镜像需要的根文件：
# pyproject.toml（settings 读 app_version）、uv.lock（锁依赖）、
# README.md（pyproject 的 readme）、run.py（入口）
PROJECT_FILES = ('pyproject.toml', 'uv.lock', 'README.md', 'run.py')

# --cn 时使用的国内镜像
CN_PIP_INDEX = 'https://mirrors.ustc.edu.cn/pypi/simple'
CN_NPM_REGISTRY = 'https://registry.npmmirror.com'


def _copy_tree(src: Path, dst: Path, ignores: tuple[str, ...] = ()) -> None:
    """递归复制目录；`symlinks=False` 会把模块目录链接解引用成真实目录。"""
    shutil.copytree(
        src,
        dst,
        symlinks=False,  # 跟随软链接：模块目录在这里被物化
        ignore=shutil.ignore_patterns(*ignores) if ignores else None,
        dirs_exist_ok=True,
    )


def _copy_file(rel: str) -> None:
    """复制仓库根下的单个文件到构建上下文（保持相对路径）。"""
    src = ROOT / rel
    dst = BUILD_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _prepare() -> None:
    """重建 docker/build，组装一份完整的临时项目。

    结果（两个镜像共用同一个上下文）：
        docker/build/
        ├── app/                     平台后端 + app/<module>
        ├── web/                     平台前端 + web/src/features/<module>
        ├── docker/nginx/default.conf
        ├── pyproject.toml
        ├── uv.lock
        ├── README.md
        └── run.py

    每次先删再建，避免残留上一次的模块或文件。
    """
    print(f'==> 组装构建上下文：{BUILD_DIR}')
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    BUILD_DIR.mkdir(parents=True)

    _copy_tree(ROOT / 'app', BUILD_DIR / 'app', BACKEND_IGNORES)
    _copy_tree(ROOT / 'web', BUILD_DIR / 'web', WEB_IGNORES)
    _copy_tree(ROOT / 'docker' / 'nginx', BUILD_DIR / 'docker' / 'nginx')
    for rel in PROJECT_FILES:
        _copy_file(rel)


def _build(dockerfile: str, image: str, build_args: dict[str, str] | None = None) -> None:
    """调用 docker build；build_args 直接作为 --build-arg 透传。

    Dockerfile 从平台路径读取，构建上下文统一是 docker/build。
    """
    cmd = ['docker', 'build', '-f', dockerfile, '-t', image]
    for name, value in (build_args or {}).items():
        cmd += ['--build-arg', f'{name}={value}']
    cmd.append(BUILD_DIR.relative_to(ROOT).as_posix())

    print('==> ' + ' '.join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def build_web(cn: bool = False) -> None:
    """构建前端镜像；镜像名来自 ORANGE_WEB_IMAGE。"""
    image = os.environ.get('ORANGE_WEB_IMAGE', 'orange-web:dev')
    build_args = {'NPM_REGISTRY': CN_NPM_REGISTRY} if cn else {}
    _build('docker/Dockerfile_web', image, build_args)
    print(f'==> 完成：{image}')


def build_backend(cn: bool = False) -> None:
    """构建后端镜像；镜像名来自 ORANGE_APP_IMAGE。"""
    image = os.environ.get('ORANGE_APP_IMAGE', 'orange-app:dev')
    build_args = (
        {'PIP_INDEX_URL': CN_PIP_INDEX, 'UV_DEFAULT_INDEX': CN_PIP_INDEX}
        if cn else {}
    )
    _build('docker/Dockerfile_backend', image, build_args)
    print(f'==> 完成：{image}')


def main() -> int:
    parser = argparse.ArgumentParser(description='组装构建上下文并构建镜像')
    parser.add_argument(
        'target',
        nargs='?',
        default='all',
        choices=('web', 'backend', 'all'),
        help='构建目标（缺省 all）',
    )
    parser.add_argument('--cn', action='store_true', help='使用国内镜像源（USTC / npmmirror）')
    args = parser.parse_args()

    # all 也只组装一次上下文，两个镜像共用
    _prepare()
    if args.target in ('web', 'all'):
        build_web(cn=args.cn)
    if args.target in ('backend', 'all'):
        build_backend(cn=args.cn)
    return 0


if __name__ == '__main__':
    sys.exit(main())
