import type { AppProps } from 'next/app';
import { RecoilRoot } from 'recoil';
import { FC, PropsWithChildren } from 'react';
import { useGetUser } from '~/store/userState';
import { SnackbarProvider } from 'notistack';
import { createTheme, CssBaseline, ThemeProvider } from '@mui/material';

// Roboto fonts
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

const InitRecoilState: FC<PropsWithChildren> = ({ children }) => {
  const user = useGetUser();

  if (user === undefined) {
    return null;
  }

  return <>{children}</>;
};

function MyApp({ Component, pageProps }: AppProps) {
  const theme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#2e8c83',
      },
    },
  });

  return (
    <RecoilRoot>
      <InitRecoilState>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <SnackbarProvider
            maxSnack={5}
            autoHideDuration={3000}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Component {...pageProps} />
          </SnackbarProvider>
        </ThemeProvider>
      </InitRecoilState>
    </RecoilRoot>
  );
}

export default MyApp;
