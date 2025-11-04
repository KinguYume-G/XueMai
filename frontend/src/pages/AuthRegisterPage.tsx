import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/store/authStore'
import { universitiesApi } from '@/services/api/universities'
import type { University } from '@/types/auth'

// 本地表单状态（前端使用 passwordConfirm，提交时转换为 password_confirm）
interface FormState {
  username: string
  email: string
  password: string
  passwordConfirm: string
}

const initialForm: FormState = {
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
}

export default function AuthRegisterPage() {
  const navigate = useNavigate()
  // ✅ 分别选择，避免创建新对象
  const register = useAuthStore((state) => state.register)
  const loading = useAuthStore((state) => state.loading)

  const [form, setForm] = useState<FormState>(initialForm)
  const [selectedUniversity, setSelectedUniversity] = useState<number | undefined>(undefined)
  const [universities, setUniversities] = useState<University[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const fetchUniversities = async () => {
      try {
        const data = await universitiesApi.list()
        if (mounted) {
          setUniversities(data)
        }
      } catch (err) {
        // 默默忽略，保留一个空列表
      }
    }

    fetchUniversities()

    return () => {
      mounted = false
    }
  }, [])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleUniversityChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const { value } = event.target
    setSelectedUniversity(value ? Number(value) : undefined)
  }

  const passwordsMatch = useMemo(
    () => form.password && form.passwordConfirm && form.password === form.passwordConfirm,
    [form.password, form.passwordConfirm],
  )

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    if (form.password !== form.passwordConfirm) {
      setError('两次输入的密码不一致')
      return
    }

    try {
      await register({
        username: form.username,
        email: form.email,
        password: form.password,
        password_confirm: form.passwordConfirm, // ✅ 后端要求的字段名
        university: selectedUniversity,
      })
      navigate('/login', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '注册失败，请稍后重试')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 px-4">
      <div className="w-full max-w-xl rounded-2xl border bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold">注册学脉账号</h1>
        <p className="mt-2 text-sm text-muted-foreground">加入泛亚高校网络，和同学们一起交流成长。</p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="username">
              用户名
            </label>
            <Input
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="请输入用户名"
              autoComplete="username"
              required
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="email">
                邮箱
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                placeholder="school@email.com"
                autoComplete="email"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="university">
                所属院校（可选）
              </label>
              <select
                id="university"
                name="university"
                value={selectedUniversity ?? ''}
                onChange={handleUniversityChange}
                className="h-11 w-full rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="">暂不选择</option>
                {universities.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="password">
                密码
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder="至少 8 位"
                autoComplete="new-password"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="passwordConfirm">
                确认密码
              </label>
              <Input
                id="passwordConfirm"
                name="passwordConfirm"
                type="password"
                value={form.passwordConfirm}
                onChange={handleChange}
                placeholder="再次输入密码"
                autoComplete="new-password"
                required
              />
              {form.passwordConfirm && !passwordsMatch ? (
                <p className="text-xs text-destructive">两次输入的密码不一致</p>
              ) : null}
            </div>
          </div>

          {error ? <p className="text-sm text-destructive">{error}</p> : null}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? '注册中...' : '注册'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          已有账号？
          <Link to="/login" className="ml-1 font-medium text-primary hover:underline">
            立即登录
          </Link>
        </p>
      </div>
    </div>
  )
}


