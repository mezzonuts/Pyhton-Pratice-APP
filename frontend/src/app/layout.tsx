import './globals.css'
import { TailwindProvider } from '@/components/uI/tailwind-provider'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'PyForge',
  description: 'PyForge frontend dashboard',
}

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <TailwindProvider>
          <nav className="border-b bg-background px-4 py-2">
            <div className="flex items-center justify-between max-w-7xl mx-auto">
              <h1 className="text-xl font-bold">PyForge</h1>
              <div className="flex items-center gap-4">
                <span className="text-sm text-muted-foreground">User</span>
                <div className="relative w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                </div>
              </div>
            </div>
          </nav>
          <main className="py-8">{children}</main>
        </TailwindProvider>
      </body>
    </html>
  )
}