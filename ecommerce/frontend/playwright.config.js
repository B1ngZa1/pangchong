import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 45_000,
  expect: {
    timeout: 8_000,
    toHaveScreenshot: {
      animations: 'disabled',
      caret: 'hide',
      maxDiffPixelRatio: 0.01,
    },
  },
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  snapshotPathTemplate: '{testDir}/snapshots/{projectName}/{arg}{ext}',
  use: {
    baseURL: 'http://127.0.0.1:3000',
    colorScheme: 'dark',
    locale: 'zh-CN',
    deviceScaleFactor: 1,
    launchOptions: {
      args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
    },
  },
  projects: [
    { name: 'mobile-360', use: { viewport: { width: 360, height: 844 } } },
    { name: 'mobile-390', use: { viewport: { width: 390, height: 844 } } },
    { name: 'mobile-430', use: { viewport: { width: 430, height: 932 } } },
  ],
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1',
    url: 'http://127.0.0.1:3000/diy',
    reuseExistingServer: true,
    timeout: 120_000,
  },
})
