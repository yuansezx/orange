import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      // 模块边界守卫（对应后端「模块根不发布内部」）：
      //  1. 跨 feature 只能经门面 @features/<name>，禁止深入内部路径；
      //  2. feature / shared 不得反向依赖组合根 app。
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['@features/*/**'],
              message: '跨 feature 只能经其门面导入（@features/<name>），禁止深入内部路径。',
            },
            {
              group: ['@app', '@app/**'],
              message: 'app 是组合根，只能向下依赖；feature / shared 不得反向依赖 app。',
            },
          ],
        },
      ],
    },
  },
])
