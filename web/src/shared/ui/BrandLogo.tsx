import { appConfig } from '@shared/config'

/** 品牌图标（`public/logo.svg`）——各处统一用它，尺寸可调。 */
export function BrandLogo({ size = 24 }: { size?: number }) {
  return <img src="/logo.svg" alt={appConfig.name} width={size} height={size} />
}
