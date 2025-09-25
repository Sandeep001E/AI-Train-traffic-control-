import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

// MUI theme setup
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import '@fontsource-variable/inter'

const theme = createTheme({
  palette: {
    background: { default: '#f5f7fb' },
  },
  typography: {
    fontFamily: 'Inter, system-ui, Arial',
  },
  shape: { borderRadius: 10 },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
)
