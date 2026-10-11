/**
 * 后端未就绪时，dev 下默认用 mock 数据先行开发。
 * 关闭：设 `VITE_USE_MOCK=false`；生产构建（DEV=false）永不启用 mock。
 */
export const USE_MOCK = import.meta.env.DEV && import.meta.env.VITE_USE_MOCK !== 'false'
