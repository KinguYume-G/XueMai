import type { User } from './api'

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
  password_confirm: string
  university?: number
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface University {
  id: number
  name: string
}

export type { User }


