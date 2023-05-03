// Roboto fonts
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import type { AppProps } from 'next/app';
import { RecoilRoot } from 'recoil';
import { FC, PropsWithChildren } from 'react';
import { useGetUser } from '~/store/userState';
import { SnackbarProvider } from 'notistack';
import { createTheme, CssBaseline, ThemeProvider } from '@mui/material';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { ConfirmDialog } from '~/components/dialogs/ConfirmDialog';
import { useGetIncompleteTasks } from '~/store/tasksState';
import { styled } from '@mui/material';

const StyledSnackbarProvider = styled(SnackbarProvider)`
  &.SnackbarItem-contentRoot {
    margin-top: 48px;
    margin-bottom: -48px;
  }
`;

const InitRecoilState: FC<PropsWithChildren> = ({ children }) => {
  const user = useGetUser();
  const { confirmDialogProps } = useConfirmDialog();
  useGetIncompleteTasks();

  if (user === undefined) {
    return null;
  }

  return (
    <>
      <ConfirmDialog {...confirmDialogProps} />
      {children}
    </>
  );
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
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <RecoilRoot>
        <InitRecoilState>
          <StyledSnackbarProvider
            maxSnack={5}
            autoHideDuration={3000}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Component {...pageProps} />
          </StyledSnackbarProvider>
        </InitRecoilState>
      </RecoilRoot>
    </ThemeProvider>
  );
}

export default MyApp;
