import type { Theme } from '@mui/material/styles';
import { createTheme } from '@mui/material/styles';

export default function createCustomTheme(): Theme {
  return createTheme({
    components: componentStyleOverrides(),
    palette: {
      primary: { main: '#2A2A7D' },
      secondary: { main: '#6639ba' },
    },
    shape: {
      borderRadius: '0.5rem' as any,
    },
  });
}

function componentStyleOverrides() {
  return {
    MuiAppBar: {
      styleOverrides: {
        colorPrimary: {
          backgroundColor: '#32383f',
        },
      },
    },
  };
}
