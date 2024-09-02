import CssBaseline from '@mui/material/CssBaseline';
import StyledEngineProvider from '@mui/material/StyledEngineProvider';
import { ThemeProvider } from '@mui/material/styles';
import { useMemo, type ReactNode } from 'react';

import { AuthProvider } from 'contexts/AuthContext';
import { CustomizationProvider } from 'contexts/CustomizationContext';
import Locales from 'locales';
import Routes from 'routes';
import createCustomTheme from 'theme';

export default function App(): ReactNode {
  const theme = useMemo(createCustomTheme, []);
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Locales>
          <AuthProvider>
            <CustomizationProvider>
              <Routes />
            </CustomizationProvider>
          </AuthProvider>
        </Locales>
      </ThemeProvider>
    </StyledEngineProvider>
  );
}
