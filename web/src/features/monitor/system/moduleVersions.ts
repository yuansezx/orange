/**
 * 非平台模块的前端版本——约定放在 `web/src/features/<module>/package.json`。
 * 平台内置 feature（iam / monitor）没有该文件，自然不进入列表。
 */
interface ModulePackageJson {
  name?: string
  version?: string
}

const discovered = import.meta.glob<ModulePackageJson>('../../*/package.json', {
  eager: true,
  import: 'default',
})

export const frontendModuleVersions: Record<string, string> = Object.fromEntries(
  Object.entries(discovered).flatMap(([path, pkg]) => {
    const name = path.split('/').at(-2)
    return name && pkg.version ? [[name, pkg.version] as const] : []
  }),
)
