import type { AppProps } from 'next/app';
import { RecoilRoot } from 'recoil';
import { FC, PropsWithChildren } from 'react';
import { useGetUser } from '~/store/userState';

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
        <Component {...pageProps} />
      </InitRecoilState>
    </RecoilRoot>
  );
}

export default MyApp;
