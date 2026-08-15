import { API_BASE_URL } from '@/lib/api/client'
import { getAccessToken } from '@/lib/auth/token'
import type { ChatMessage } from '@/types/chat'

export type PresenceEvent = {
  user_id: number
  is_online: boolean
  last_seen?: string | null
}

export type ChatSocketEvent =
  | { type: 'message.created'; payload: ChatMessage }
  | { type: 'presence.changed'; payload: PresenceEvent }
  | { type: 'notification.created'; payload: unknown }
  | { type: 'error'; message?: string }

type Listener = (event: ChatSocketEvent) => void

class ChatSocket {
  private socket: WebSocket | null = null
  private listeners = new Set<Listener>()
  private reconnectTimer: number | null = null
  private shouldReconnect = false

  connect() {
    const token = getAccessToken()
    if (!token || this.socket?.readyState === WebSocket.OPEN) return

    this.shouldReconnect = true
    const apiUrl = new URL(API_BASE_URL)
    const protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${apiUrl.host}/ws/chat/?token=${encodeURIComponent(token)}`

    this.socket = new WebSocket(url)
    this.socket.onmessage = (message) => {
      const event = JSON.parse(message.data) as ChatSocketEvent
      this.listeners.forEach((listener) => listener(event))
    }
    this.socket.onclose = () => {
      this.socket = null
      if (this.shouldReconnect) {
        this.reconnectTimer = window.setTimeout(() => this.connect(), 3000)
      }
    }
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.reconnectTimer !== null) window.clearTimeout(this.reconnectTimer)
    this.reconnectTimer = null
    this.socket?.close()
    this.socket = null
  }

  subscribe(listener: Listener) {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  sendMessage(payload: {
    to_user_id?: number
    group_id?: number
    content: string
    message_type: 'text' | 'image' | 'file' | 'emoji'
  }) {
    if (this.socket?.readyState !== WebSocket.OPEN) return false
    this.socket.send(JSON.stringify({ type: 'message.send', payload }))
    return true
  }
}

export const chatSocket = new ChatSocket()
