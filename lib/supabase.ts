import { createBrowserClient } from '@supabase/ssr'

let supabase: SupabaseClient | null = null

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

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
