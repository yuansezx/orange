/** 模块后端版本——对齐后端 `ModuleVersionResp`。 */
export interface ModuleVersion {
  name: string
  version: string
}

/** 平台/模块版本快照——对齐后端 `SystemVersionsResp`。 */
export interface SystemVersions {
  platform_version: string
  modules: ModuleVersion[]
}

/** 页面合并后的模块版本行（后端 + 前端两侧按模块名对齐）。 */
export interface ModuleVersionRow {
  name: string
  backend_version: string | null
  frontend_version: string | null
}
