import type { AppProps } from 'next/app';
import { RecoilRoot } from 'recoil';
import { FC, PropsWithChildren } from 'react';
import { useGetUser } from '~/store/userState';
import { SnackbarProvider } from 'notistack';

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
  return (
    <RecoilRoot>
      <InitRecoilState>
        <SnackbarProvider maxSnack={5} autoHideDuration={3000} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
          <Component {...pageProps} />
        </SnackbarProvider>
      </InitRecoilState>
    </RecoilRoot>
  );
}

export default MyApp;
