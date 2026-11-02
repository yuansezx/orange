import { buildAntdTheme } from '@shared/theme/antdTheme'
import { defaultWorkspacePalette } from '@shared/theme/tokens'

/**
 * 全局主题（系统壳 + 默认 workspace）：用默认 workspace 调色板映射，
 * 保证系统壳与 workspace 缺省观感一致。各 workspace 在 `WorkspaceThemeProvider`
 * 里用合并后的调色板覆盖；系统壳在 provider 之外，始终走这份全局品牌配色。
 */
export const antdTheme = buildAntdTheme(defaultWorkspacePalette)
