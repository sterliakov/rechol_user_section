import { createTheme, Theme, ThemeProvider } from '@mui/material/styles';

export default function createCustomTheme() {
    return createTheme({components: componentStyleOverrides()});
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
          MuiInputBase: {
              styleOverrides: {
                  input: {
                      // color: theme.palette.text,
                      '&::placeholder': {
                          // color: theme.palette.darkTextSecondary,
                          fontSize: '0.875rem',
                      },
                  },
              },
          },
          // MuiInputLabel: {
          //     styleOverrides: {
          //         root: {
          //             color: muiColors.grey[700],
          //         },
          //     },
          // },
          MuiOutlinedInput: {
              styleOverrides: {
                  root: {
                      background: 'transparent',
                      borderRadius: '0.5rem',
                      },
                      '&.MuiInputBase-multiline': {
                          padding: 1,
                      },
                  },
                  input: {
                      fontWeight: 500,
                      background: 'transparent',
                      padding: '15.5px 14px',
                      borderRadius: '0.5rem',
                      '&.MuiInputBase-inputSizeSmall': {
                          padding: '10px 14px',
                          '&.MuiInputBase-inputAdornedStart': {
                              paddingLeft: 0,
                          },
                      },
                  },
                  inputAdornedStart: {
                      paddingLeft: 4,
                  },
                  notchedOutline: {
                      borderRadius: '0.5rem',
                  },
              },
          };
}
