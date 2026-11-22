"""组装 Docker 构建上下文并构建镜像（构建工具，不属于平台 scripts）。

为什么需要组装：
平台通过目录链接引入仓外模块（app/<module>、web/src/features/<module>），
Docker 不会跟随指向构建上下文之外的软链接。这里把链接解引用成真实目录，
再让 Docker 用普通上下文构建，避免 named context、逐模块参数和 .dockerignore 里的模块名单。

用法（在仓库根执行）：
    uv run python docker/build_images.py all      # web + app
    uv run python docker/build_images.py web
    uv run python docker/build_images.py app

产物：
    docker/build/            临时完整项目；构建前重建，构建后可删

构建参数：
    --app-image / --web-image   镜像名；缺省读 ORANGE_APP_IMAGE / ORANGE_WEB_IMAGE，再缺省 nightly
    --platform                  目标平台（如 linux/amd64）；缺省跟随构建机
    --proxy                     构建容器使用的 HTTP/HTTPS 代理（如 http://host.docker.internal:10002）
    --cn                        使用国内镜像源（pip/uv: USTC，npm: npmmirror）
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


def _build(
    dockerfile: str,
    image: str,
    build_args: dict[str, str] | None = None,
    platform: str | None = None,
) -> None:
    """调用 docker build；build_args 直接作为 --build-arg 透传。

    platform 为空时跟随构建机架构；Dockerfile 从平台路径读取，上下文统一是 docker/build。
    """
    cmd = ['docker', 'build']
    if platform:
        cmd += ['--platform', platform]
    cmd += ['-f', dockerfile, '-t', image]
    for name, value in (build_args or {}).items():
        cmd += ['--build-arg', f'{name}={value}']
    cmd.append(BUILD_DIR.relative_to(ROOT).as_posix())

    print('==> ' + ' '.join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def _proxy_args(proxy: str | None) -> dict[str, str]:
    """构建容器的 HTTP/HTTPS 代理参数；只影响 RUN 阶段，不影响 FROM metadata。"""
    if not proxy:
        return {}
    return {
        'HTTP_PROXY': proxy,
        'HTTPS_PROXY': proxy,
        'NO_PROXY': 'localhost,127.0.0.1',
    }


def build_web(
    image: str,
    cn: bool = False,
    platform: str | None = None,
    proxy: str | None = None,
) -> None:
    """构建前端镜像。"""
    build_args = _proxy_args(proxy)
    if cn:
        build_args['NPM_REGISTRY'] = CN_NPM_REGISTRY
    _build('docker/Dockerfile_web', image, build_args, platform)
    print(f'==> 完成：{image}')


def build_app(
    image: str,
    cn: bool = False,
    platform: str | None = None,
    proxy: str | None = None,
) -> None:
    """构建 app（后端）镜像。"""
    build_args = _proxy_args(proxy)
    if cn:
        build_args['PIP_INDEX_URL'] = CN_PIP_INDEX
        build_args['UV_DEFAULT_INDEX'] = CN_PIP_INDEX
    _build('docker/Dockerfile_app', image, build_args, platform)
    print(f'==> 完成：{image}')


def main() -> int:
    parser = argparse.ArgumentParser(description='组装构建上下文并构建镜像')
    parser.add_argument(
        'target',
        nargs='?',
        default='all',
        choices=('web', 'app', 'all'),
        help='构建目标（缺省 all）',
    )
    parser.add_argument(
        '--app-image',
        default=os.environ.get('ORANGE_APP_IMAGE', 'orange-app:nightly'),
        help='后端镜像名（缺省读 ORANGE_APP_IMAGE）',
    )
    parser.add_argument(
        '--web-image',
        default=os.environ.get('ORANGE_WEB_IMAGE', 'orange-web:nightly'),
        help='前端镜像名（缺省读 ORANGE_WEB_IMAGE）',
    )
    parser.add_argument(
        '--platform',
        default=None,
        help='目标平台，如 linux/amd64（缺省跟随构建机）',
    )
    parser.add_argument(
        '--proxy',
        default=None,
        help='构建容器使用的 HTTP/HTTPS 代理，如 http://host.docker.internal:10002',
    )
    parser.add_argument('--cn', action='store_true', help='使用国内镜像源（USTC / npmmirror）')
    args = parser.parse_args()

    # all 也只组装一次上下文，两个镜像共用
    _prepare()
    if args.target in ('web', 'all'):
        build_web(args.web_image, cn=args.cn, platform=args.platform, proxy=args.proxy)
    if args.target in ('app', 'all'):
        build_app(args.app_image, cn=args.cn, platform=args.platform, proxy=args.proxy)
    return 0


if __name__ == '__main__':
    sys.exit(main())
