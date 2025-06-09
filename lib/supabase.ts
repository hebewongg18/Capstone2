import { createClient } from '@supabase/supabase-js'
import type { SupabaseClient } from '@supabase/supabase-js'

let supabase: SupabaseClient | null = null

export const getSupabase = () => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  console.log("🔍 ENV:", {
    url,
    key: key?.slice(0, 10) + "..."
  })

  if (!url || !key) {
    throw new Error('Missing Supabase environment variables')
  }

  if (!supabase) {
    supabase = createClient(url, key)
  }

  return supabase
}
