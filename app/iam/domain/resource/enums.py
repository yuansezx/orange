from enum import Enum


class SourceTypeEnum(str, Enum):
    """资源 / 权限的来源。

    `SYSTEM` = 代码声明（bootstrap 拥有，可对其做「声明没了就停用」的对账）；
    `CUSTOM` = 后台自建（对账不得触碰）。
    """
    SYSTEM = "system"
    CUSTOM = "custom"
