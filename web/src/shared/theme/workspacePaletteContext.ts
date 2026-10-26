import { createContext, useContext } from 'react'

import { defaultWorkspacePalette } from './tokens'
import type { WorkspacePalette } from './tokens'

export const WorkspacePaletteContext =
  createContext<WorkspacePalette>(defaultWorkspacePalette)

/** workspace 内取调色板（内联样式用）；不在 provider 内时回退默认调色板。 */
export function useWorkspacePalette(): WorkspacePalette {
  return useContext(WorkspacePaletteContext)
}
