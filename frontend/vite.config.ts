import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    //port: 5173
    proxy:
    {
      '/api':{
        target:'https://tricky-boxes-prove.loca.lt/api',
        changeOrigin:true,
        secure:false,
        rewrite: (path)  => path.replace(/^\/api/, '')

      }
    }
  },
  plugins: [react()],
  build: {
    outDir: 'dist'
  }
})
