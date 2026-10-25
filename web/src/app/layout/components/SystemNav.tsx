import { Button, Tooltip, theme } from 'antd'
import { Link } from 'react-router-dom'

import { UserMenu } from '@features/auth'
import { appConfig } from '@shared/config'
import { colorTokens } from '@shared/theme/tokens'
import {
  BrandLogo,
  IconBox,
  IconChevronLeft,
  IconChevronRight,
  IconChevronsLeft,
} from '@shared/ui'

import type { WorkspaceNav } from '../../routes'

interface Props {
  workspaces: WorkspaceNav[]
  currentWorkspaceKey?: string
  state: 'rail' | 'expanded'
  canHide: boolean
  onSelectWorkspace: (workspace: WorkspaceNav) => void
  onCollapse: () => void
  onExpand: () => void
  onHide: () => void
}

const iconItemStyle = {
  width: 40,
  height: 40,
  padding: 0,
} as const

/** 系统级导航：rail（纯图标）/ expanded（带名称）两种形态。 */
export function SystemNav({
  workspaces,
  currentWorkspaceKey,
  state,
  canHide,
  onSelectWorkspace,
  onCollapse,
  onExpand,
  onHide,
}: Props) {
  const { token } = theme.useToken()
  const expanded = state === 'expanded'

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div
        style={{
          height: 56,
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          paddingInline: expanded ? 12 : 2,
        }}
      >
        <Link
          to="/"
          aria-label="返回默认页面"
          style={{
            flex: 1,
            minWidth: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: expanded ? 'flex-start' : 'center',
            gap: 10,
            color: colorTokens.brand,
            textDecoration: 'none',
            fontSize: 16,
            fontWeight: 600,
          }}
        >
          <BrandLogo size={26} />
          {expanded && (
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {appConfig.name}
            </span>
          )}
        </Link>
        <Tooltip title={expanded ? '收起为图标栏' : '展开系统栏'}>
          <Button
            type="text"
            size="small"
            aria-label={expanded ? '收起为图标栏' : '展开系统栏'}
            icon={expanded ? <IconChevronLeft size={16} /> : <IconChevronRight size={14} />}
            onClick={expanded ? onCollapse : onExpand}
            style={
              expanded
                ? undefined
                : { width: 24, height: 24, padding: 0, flexShrink: 0 }
            }
          />
        </Tooltip>
      </div>

      <div
        style={{
          flex: 1,
          minHeight: 0,
          overflow: 'auto',
          paddingBlock: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: expanded ? 'stretch' : 'center',
          gap: 4,
          paddingInline: expanded ? 8 : 0,
        }}
      >
        {workspaces.map((workspace) => {
          const active = workspace.key === currentWorkspaceKey
          const content = (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                minWidth: 0,
              }}
            >
              <span style={{ display: 'inline-flex', flexShrink: 0 }}>
                {workspace.icon ?? <IconBox size={20} />}
              </span>
              {expanded && (
                <span
                  style={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {workspace.label}
                </span>
              )}
            </div>
          )

          const button = (
            <Button
              type="text"
              aria-label={workspace.label}
              onClick={() => onSelectWorkspace(workspace)}
              style={{
                ...(expanded
                  ? { width: '100%', height: 40, justifyContent: 'flex-start', paddingInline: 12 }
                  : iconItemStyle),
                color: active ? colorTokens.brand : token.colorTextSecondary,
                background: active ? token.colorFillSecondary : undefined,
              }}
            >
              {content}
            </Button>
          )

          return expanded ? (
            <div key={workspace.key}>{button}</div>
          ) : (
            <Tooltip key={workspace.key} title={workspace.label} placement="right">
              {button}
            </Tooltip>
          )
        })}
      </div>

      <div
        style={{
          flexShrink: 0,
          borderTop: `1px solid ${colorTokens.borderSecondary}`,
          padding: 8,
          display: 'flex',
          flexDirection: expanded ? 'row' : 'column',
          alignItems: 'center',
          gap: 4,
        }}
      >
        <div style={{ flex: expanded ? 1 : undefined, minWidth: 0 }}>
          <UserMenu placement="topLeft" compact={!expanded} />
        </div>
        {canHide && (
          <Tooltip title="隐藏系统栏">
            <Button
              type="text"
              size="small"
              aria-label="隐藏系统栏"
              icon={<IconChevronsLeft size={16} />}
              onClick={onHide}
            />
          </Tooltip>
        )}
      </div>
    </div>
  )
}
