from pydantic import BaseModel
from ua_parser import parse


class UserAgentInfo(BaseModel):
    """UA 解析结果（仅用于展示，原始 UA 另行保留）。"""
    browser: str | None = None
    browser_version: str | None = None
    os: str | None = None
    device: str | None = None


def parse_user_agent(user_agent: str | None) -> UserAgentInfo:
    if not user_agent:
        return UserAgentInfo()
    result = parse(user_agent)
    return UserAgentInfo(
        browser=_family(result.user_agent),
        browser_version=_version(result.user_agent),
        os=_family(result.os),
        device=_family(result.device),
    )


def _family(part) -> str | None:
    return part.family if part else None


def _version(part) -> str | None:
    if not part:
        return None
    # 1.x 把版本拆成四段；遇到第一个空段即截断，避免拼出 "1..2"
    segments: list[str] = []
    for segment in (part.major, part.minor, part.patch, part.patch_minor):
        if not segment:
            break
        segments.append(segment)
    return '.'.join(segments) or None
