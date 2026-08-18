import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
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
  const { t } = useTranslation()
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
      setError(t('auth.register.passwordMismatch'))
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
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.register.genericError'))
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 px-4">
      <div className="w-full max-w-xl rounded-2xl border bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold">{t('auth.register.title')}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{t('auth.register.subtitle')}</p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="username">
              {t('auth.register.usernameLabel')}
            </label>
            <Input
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder={t('auth.register.usernamePlaceholder')}
              autoComplete="username"
              required
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="email">
                {t('auth.register.emailLabel')}
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
                {t('auth.register.universityLabel')}
              </label>
              <select
                id="university"
                name="university"
                value={selectedUniversity ?? ''}
                onChange={handleUniversityChange}
                className="h-11 w-full rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="">{t('auth.register.universityPlaceholder')}</option>
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
                {t('auth.register.passwordLabel')}
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder={t('auth.register.passwordPlaceholder')}
                autoComplete="new-password"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="passwordConfirm">
                {t('auth.register.passwordConfirmLabel')}
              </label>
              <Input
                id="passwordConfirm"
                name="passwordConfirm"
                type="password"
                value={form.passwordConfirm}
                onChange={handleChange}
                placeholder={t('auth.register.passwordConfirmPlaceholder')}
                autoComplete="new-password"
                required
              />
              {form.passwordConfirm && !passwordsMatch ? (
                <p className="text-xs text-destructive">{t('auth.register.passwordMismatch')}</p>
              ) : null}
            </div>
          </div>

          {error ? <p className="text-sm text-destructive">{error}</p> : null}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? t('auth.register.submitting') : t('auth.register.submit')}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          {t('auth.register.haveAccount')}
          <Link to="/login" className="ml-1 font-medium text-primary hover:underline">
            {t('auth.register.loginLink')}
          </Link>
        </p>
      </div>
    </div>
  )
}

