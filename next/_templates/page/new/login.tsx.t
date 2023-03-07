---
to: "<%= pageType === 'login' ? `pages/${url}.tsx` : null %>"
---

import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty</title>
      </Head>
    </DefaultLayout>
  );
};

export default Page;
