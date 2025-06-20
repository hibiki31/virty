import { GetServerSideProps, GetServerSidePropsResult, PreviewData } from 'next';
import nookies from 'nookies';
import { ParsedUrlQuery } from 'querystring';
import { authApi } from '../api';

export const makeRequireLoginProps =
  <P extends { [key: string]: any }, Q extends ParsedUrlQuery = ParsedUrlQuery, D extends PreviewData = PreviewData>(
    getServerSideProps?: GetServerSideProps<P, Q, D>
  ): GetServerSideProps<P, Q, D> =>
  async (ctx) => {
    const { token } = nookies.get(ctx);
    const isValid = await authApi
      .validateToken({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then(() => true)
      .catch(() => false);

    if (!isValid) {
      nookies.destroy(ctx, 'token', { path: '/' });
      return {
        redirect: {
          destination: '/login',
          permanent: false,
        },
      };
    }

    if (!getServerSideProps) {
      return {
        props: {},
      } as GetServerSidePropsResult<P>;
    }

    return getServerSideProps(ctx);
  };

export const makeRequireLogoutProps =
  <P extends { [key: string]: any }, Q extends ParsedUrlQuery = ParsedUrlQuery, D extends PreviewData = PreviewData>(
    getServerSideProps?: GetServerSideProps<P, Q, D>
  ): GetServerSideProps<P, Q, D> =>
  async (ctx) => {
    const { token } = nookies.get(ctx);
    const isValid = await authApi
      .validateToken({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then(() => true)
      .catch(() => false);

    if (isValid) {
      return {
        redirect: {
          destination: '/',
          permanent: false,
        },
      };
    }

    nookies.destroy(ctx, 'token', { path: '/' });
    if (!getServerSideProps) {
      return {
        props: {},
      } as GetServerSidePropsResult<P>;
    }

    return getServerSideProps(ctx);
  };
