import type { NextPage } from 'next';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const HomePage: NextPage = () => {
  return <div>Virty</div>;
};

export default HomePage;
