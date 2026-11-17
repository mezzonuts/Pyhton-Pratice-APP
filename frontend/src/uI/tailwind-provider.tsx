import { CssBaseline } from '@mui/material'
import { ThemeProvider as NextThemedProvider } from 'next-themes'
import { ReactNode } from 'react'

export const TailwindProvider = ({
  children,
}: {
  children: ReactNode
}) => {
  return (
    <NextThemedProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
    >
      {children}
    </NextThemedProvider>
  )
}