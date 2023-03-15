import { createTheme, CssBaseline, ThemeProvider } from '@mui/material';
import { RecoilRoot } from 'recoil';

export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};

export const decorators = [
  (Story) => {
    const theme = createTheme({
      palette: {
        mode: 'dark',
        primary: {
          main: '#2e8c83',
        },
      },
    });
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <RecoilRoot>
          <Story />
        </RecoilRoot>
      </ThemeProvider>
    );
  },
];
