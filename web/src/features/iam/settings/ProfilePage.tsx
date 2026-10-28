import {
  Alert,
  App,
  Button,
  Card,
  Dropdown,
  Modal,
  Space,
  Tag,
  Typography,
} from 'antd'
import dayjs from 'dayjs'
import { useEffect, useRef, useState } from 'react'
import type { ChangeEvent, ReactNode, SyntheticEvent } from 'react'
import ReactCrop from 'react-image-crop'
import type { Crop, PixelCrop } from 'react-image-crop'
import 'react-image-crop/dist/ReactCrop.css'
import { useNavigate } from 'react-router-dom'

import { colorTokens } from '@shared/theme/tokens'
import {
  IconCalendar,
  IconCamera,
  IconDots,
  IconEdit,
  IconKey,
  IconMail,
  IconPhone,
  IconSitemap,
  IconShieldLock,
  IconTrash,
  UserAvatar,
} from '@shared/ui'

import { USER_TYPE_LABELS } from '../user/constants'
import { EditProfileModal } from './components/EditProfileModal'
import {
  useDeleteMyAvatar,
  useMyProfile,
  useUploadMyAvatar,
} from './hooks/useMyProfile'
import type { MyProfile } from './types'

const AVATAR_MAX_BYTES = 5 * 1024 * 1024

const formatTime = (value: string | null) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'

const AVATAR_OUTPUT_SIZE = 512

/** 把裁剪区域画到 512×512 canvas，导出静态 WebP。 */
function cropToBlob(image: HTMLImageElement, crop: PixelCrop): Promise<Blob> {
  const scaleX = image.naturalWidth / image.width
  const scaleY = image.naturalHeight / image.height
  const canvas = document.createElement('canvas')
  canvas.width = AVATAR_OUTPUT_SIZE
  canvas.height = AVATAR_OUTPUT_SIZE
  const ctx = canvas.getContext('2d')
  if (!ctx) return Promise.reject(new Error('无法创建画布'))
  ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(
    image,
    crop.x * scaleX,
    crop.y * scaleY,
    crop.width * scaleX,
    crop.height * scaleY,
    0,
    0,
    AVATAR_OUTPUT_SIZE,
    AVATAR_OUTPUT_SIZE,
  )
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error('裁剪失败'))),
      'image/webp',
      0.9,
    )
  })
}

/** 淡色图标底 + 标签/值的信息块。 */
function InfoItem({
  icon,
  label,
  children,
}: {
  icon: ReactNode
  label: string
  children: ReactNode
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, minWidth: 0 }}>
      <div
        style={{
          width: 34,
          height: 34,
          borderRadius: 10,
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: colorTokens.brandSoft,
          color: colorTokens.brandAction,
        }}
      >
        {icon}
      </div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 12, color: colorTokens.textSecondary, marginBottom: 2 }}>
          {label}
        </div>
        <div style={{ minWidth: 0 }}>{children}</div>
      </div>
    </div>
  )
}

function ProfileHero({
  profile,
  onEdit,
  onSecurity,
  onPickAvatar,
  onRemoveAvatar,
  uploading,
  removing,
}: {
  profile: MyProfile
  onEdit: () => void
  onSecurity: () => void
  onPickAvatar: () => void
  onRemoveAvatar: () => void
  uploading: boolean
  removing: boolean
}) {
  return (
    <Card styles={{ body: { padding: 0 } }}>
      <div
        style={{
          height: 112,
          background: `linear-gradient(120deg, ${colorTokens.brandSoft} 0%, ${colorTokens.bgMuted} 55%, ${colorTokens.bgLayout} 100%)`,
        }}
      />
      <div style={{ padding: '0 24px 24px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-end',
            gap: 16,
            marginTop: -40,
            flexWrap: 'wrap',
          }}
        >
          <button
            type="button"
            aria-label="更换头像"
            onClick={onPickAvatar}
            disabled={uploading}
            style={{
              position: 'relative',
              flexShrink: 0,
              padding: 4,
              border: 'none',
              borderRadius: '50%',
              background: colorTokens.bgContainer,
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
              cursor: uploading ? 'default' : 'pointer',
              opacity: uploading ? 0.7 : 1,
            }}
          >
            <UserAvatar
              name={profile.nickname}
              src={profile.avatar_url ?? undefined}
              size={88}
            />
            <span
              style={{
                position: 'absolute',
                right: 2,
                bottom: 2,
                width: 26,
                height: 26,
                borderRadius: '50%',
                background: colorTokens.brandAction,
                color: colorTokens.brandActionText,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 6px rgba(0, 0, 0, 0.2)',
              }}
            >
              <IconCamera size={14} />
            </span>
          </button>
          <div style={{ flex: 1, minWidth: 200, paddingBottom: 4 }}>
            <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 2 }}>
              {profile.nickname}
            </div>
            <div>
              <Typography.Text type="secondary">@{profile.username}</Typography.Text>
            </div>
          </div>
          <Space size={8} wrap>
            <Button type="primary" icon={<IconEdit size={16} />} onClick={onEdit}>
              修改个人资料
            </Button>
            <Button onClick={onSecurity}>安全设置</Button>
            {profile.avatar_url && (
              <Dropdown
                trigger={['click']}
                placement="bottomRight"
                menu={{
                  items: [
                    {
                      key: 'remove',
                      label: '移除头像',
                      danger: true,
                      icon: <IconTrash size={16} />,
                      disabled: removing,
                    },
                  ],
                  onClick: ({ key }) => {
                    if (key === 'remove') onRemoveAvatar()
                  },
                }}
              >
                <Button type="text" aria-label="更多头像操作" icon={<IconDots size={18} />} />
              </Dropdown>
            )}
          </Space>
        </div>

        <Space size={8} wrap style={{ marginTop: 16 }}>
          <Typography.Text type="secondary">角色</Typography.Text>
          {profile.roles.length ? (
            profile.roles.map((role) => <Tag key={role.id}>{role.name}</Tag>)
          ) : (
            <Typography.Text type="secondary">未分配</Typography.Text>
          )}
        </Space>
      </div>
    </Card>
  )
}

function ProfileInfo({
  profile,
  onSecurity,
}: {
  profile: MyProfile
  onSecurity: () => void
}) {
  return (
    <Card title="账号信息">
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 20,
        }}
      >
        <InfoItem icon={<IconMail size={16} />} label="邮箱">
          {profile.email ?? <Typography.Text type="secondary">未绑定</Typography.Text>}
        </InfoItem>
        <InfoItem icon={<IconPhone size={16} />} label="手机号">
          {profile.phone ?? <Typography.Text type="secondary">未绑定</Typography.Text>}
        </InfoItem>
        <InfoItem icon={<IconSitemap size={16} />} label="部门">
          {profile.dept?.path ?? <Typography.Text type="secondary">未分配</Typography.Text>}
        </InfoItem>
        <InfoItem icon={<IconShieldLock size={16} />} label="用户类型">
          {USER_TYPE_LABELS[profile.user_type]}
        </InfoItem>
        <InfoItem icon={<IconCalendar size={16} />} label="创建时间">
          {formatTime(profile.created_at)}
        </InfoItem>
        <InfoItem icon={<IconKey size={16} />} label="密码">
          <Space size={6} wrap>
            <Tag color={profile.need_change_password ? 'warning' : 'success'}>
              {profile.need_change_password ? '待修改' : '已更新'}
            </Tag>
            <Typography.Text type="secondary">
              {profile.password_updated_at
                ? `上次修改 ${formatTime(profile.password_updated_at)}`
                : '从未修改'}
            </Typography.Text>
            <Typography.Link onClick={onSecurity}>修改</Typography.Link>
          </Space>
        </InfoItem>
      </div>

      {profile.description && (
        <div
          style={{
            marginTop: 20,
            paddingTop: 16,
            borderTop: `1px solid ${colorTokens.borderSecondary}`,
          }}
        >
          <div style={{ fontSize: 12, color: colorTokens.textSecondary, marginBottom: 4 }}>
            备注
          </div>
          <div>{profile.description}</div>
        </div>
      )}
    </Card>
  )
}

/** 个人资料：hero + 信息总览；编辑走弹窗。 */
export default function ProfilePage() {
  const { data, isLoading, error } = useMyProfile()
  const uploadAvatar = useUploadMyAvatar()
  const removeAvatar = useDeleteMyAvatar()
  const { message, modal } = App.useApp()
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)
  const [pickedFile, setPickedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [choiceOpen, setChoiceOpen] = useState(false)
  const [cropOpen, setCropOpen] = useState(false)
  const [crop, setCrop] = useState<Crop>()
  const [completedCrop, setCompletedCrop] = useState<PixelCrop>()
  const [cropping, setCropping] = useState(false)

  useEffect(() => {
    if (!previewUrl) return
    return () => URL.revokeObjectURL(previewUrl)
  }, [previewUrl])

  if (isLoading) return <Card loading style={{ minHeight: 260 }} />
  if (error) return <Alert type="error" message={error.message} showIcon />
  if (!data) return null

  const goSecurity = () => navigate('/account/iam/security')

  const resetPick = () => {
    setChoiceOpen(false)
    setCropOpen(false)
    setPickedFile(null)
    setPreviewUrl(null)
    setCrop(undefined)
    setCompletedCrop(undefined)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    if (file.size > AVATAR_MAX_BYTES) {
      message.error('头像不能超过 5 MB')
      event.target.value = ''
      return
    }
    setPickedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setCrop(undefined)
    setCompletedCrop(undefined)
    setCropOpen(false)
    setChoiceOpen(true)
  }

  const uploadOriginal = () => {
    if (!pickedFile) return
    uploadAvatar.mutate(pickedFile, { onSuccess: resetPick })
  }

  const handleCropImageLoad = (event: SyntheticEvent<HTMLImageElement>) => {
    const { width, height } = event.currentTarget
    const size = Math.min(width, height) * 0.8
    const next: Crop = {
      unit: 'px',
      x: (width - size) / 2,
      y: (height - size) / 2,
      width: size,
      height: size,
    }
    setCrop(next)
    setCompletedCrop(next as PixelCrop)
  }

  const handleCropConfirm = async () => {
    if (!imgRef.current || !completedCrop) {
      message.error('请先选择裁剪区域')
      return
    }
    setCropping(true)
    try {
      const blob = await cropToBlob(imgRef.current, completedCrop)
      const file = new File([blob], 'avatar.webp', { type: 'image/webp' })
      uploadAvatar.mutate(file, { onSuccess: resetPick })
    } catch {
      message.error('裁剪失败，请重试')
    } finally {
      setCropping(false)
    }
  }

  const confirmRemove = () =>
    modal.confirm({
      title: '移除头像？',
      content: '移除后将回退为昵称首字。',
      okText: '移除',
      okButtonProps: { danger: true },
      onOk: () => removeAvatar.mutateAsync(),
    })

  return (
    <>
      <Space direction="vertical" size={16} style={{ display: 'flex' }}>
        <ProfileHero
          profile={data}
          onEdit={() => setEditing(true)}
          onSecurity={goSecurity}
          onPickAvatar={() => fileInputRef.current?.click()}
          onRemoveAvatar={confirmRemove}
          uploading={uploadAvatar.isPending}
          removing={removeAvatar.isPending}
        />
        <ProfileInfo profile={data} onSecurity={goSecurity} />
        <EditProfileModal
          open={editing}
          profile={data}
          onClose={() => setEditing(false)}
        />
      </Space>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <Modal
        open={choiceOpen}
        title="使用这张图片作为头像"
        footer={null}
        width={460}
        onCancel={resetPick}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            background: colorTokens.bgLayout,
            borderRadius: 12,
            padding: 12,
          }}
        >
          {previewUrl && (
            <img
              src={previewUrl}
              alt="头像预览"
              style={{ maxWidth: '100%', maxHeight: 320, borderRadius: 8, objectFit: 'contain' }}
            />
          )}
        </div>
        <Typography.Paragraph type="secondary" style={{ marginTop: 12, fontSize: 12 }}>
          保留原图会保留 GIF / APNG 动画；裁剪为方形会输出静态图片并丢失动画。
        </Typography.Paragraph>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, flexWrap: 'wrap' }}>
          <Button onClick={resetPick}>取消</Button>
          <Button
            onClick={() => {
              setChoiceOpen(false)
              setCropOpen(true)
              setCrop(undefined)
              setCompletedCrop(undefined)
            }}
          >
            裁剪为方形
          </Button>
          <Button type="primary" loading={uploadAvatar.isPending} onClick={uploadOriginal}>
            保留原图
          </Button>
        </div>
      </Modal>

      <Modal
        open={cropOpen}
        title="裁剪头像"
        width={520}
        okText="确认并上传"
        cancelText="取消"
        confirmLoading={cropping || uploadAvatar.isPending}
        onOk={handleCropConfirm}
        onCancel={() => {
          if (!cropping && !uploadAvatar.isPending) resetPick()
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            background: colorTokens.bgLayout,
            borderRadius: 8,
            overflow: 'hidden',
            minHeight: 200,
          }}
        >
          {previewUrl && (
            <ReactCrop
              crop={crop}
              aspect={1}
              circularCrop
              ruleOfThirds
              minWidth={80}
              minHeight={80}
              onChange={(next) => setCrop(next)}
              onComplete={(next) => setCompletedCrop(next)}
            >
              <img
                ref={imgRef}
                src={previewUrl}
                alt="裁剪预览"
                style={{ maxHeight: 360, maxWidth: '100%' }}
                onLoad={handleCropImageLoad}
              />
            </ReactCrop>
          )}
        </div>
        <Typography.Paragraph type="secondary" style={{ marginTop: 12, fontSize: 12 }}>
          拖动 / 缩放取景框，输出 512×512 静态 WebP。
        </Typography.Paragraph>
      </Modal>
    </>
  )
}
