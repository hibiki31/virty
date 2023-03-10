---
to: "<%= pageType === 'simple' ? `pages/${url}.tsx` : null %>"
---

import type { NextPage } from 'next';
import Head from 'next/head';

const Page: NextPage = () => {
  return (
    <>
      <Head>
        <title>Virty</title>
      </Head>
    </>
  );
};

export default Page;
