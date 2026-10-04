import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // This allows access from your mobile device using your local IP
    port: 5173,      // Optional: specify port if you want to make sure it's 5173
  }
})
