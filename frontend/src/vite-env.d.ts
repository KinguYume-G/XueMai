/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_ANON_KEY?: string
  readonly VITE_DEBUG_ITINERARY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
