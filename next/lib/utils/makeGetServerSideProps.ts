import { GetServerSideProps, GetServerSidePropsResult, PreviewData } from 'next';
import { destroyCookie, parseCookies } from 'nookies';
import { ParsedUrlQuery } from 'querystring';
import { authApi } from '../api';

export const makeRequireLoginProps =
  <P extends { [key: string]: any }, Q extends ParsedUrlQuery = ParsedUrlQuery, D extends PreviewData = PreviewData>(
    getServerSideProps?: GetServerSideProps<P, Q, D>
  ): GetServerSideProps<P, Q, D> =>
  async (ctx) => {
    const { token } = parseCookies(ctx);
    const isValid = await authApi
      .readAuthValidateApiAuthValidateGet({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then(() => true)
      .catch(() => false);

    if (!isValid) {
      destroyCookie(ctx, 'token');
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
    const { token } = parseCookies(ctx);
    const isValid = await authApi
      .readAuthValidateApiAuthValidateGet({
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

    destroyCookie(ctx, 'token');
    if (!getServerSideProps) {
      return {
        props: {},
      } as GetServerSidePropsResult<P>;
    }

    return getServerSideProps(ctx);
  };
