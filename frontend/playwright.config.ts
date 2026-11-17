import { test, expect } from '@playwright/test'

export default {
  testDir: './src/tests/e2e',
  timeout: 30000,
  retries: 0,
  projects: [
    {
      name: 'Chromium',
      use: {
        browserName: 'chromium',
        baseURL: 'http://localhost:3000',
        headless: true
      }
    }
  ]
}