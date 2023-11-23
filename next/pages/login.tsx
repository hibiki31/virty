import { LoadingButton } from '@mui/lab';
import { Card, CardContent, CardHeader, Grid } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import type { NextPage } from 'next';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { NoAuthLayout } from '~/components/layouts/NoAuthLayout';
import { mixinApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { makeRequireLogoutProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';
import { useAuth } from '~/store/userState';

type LoginForm = JTDDataType<typeof loginFormJtd>;

export const getServerSideProps = makeRequireLogoutProps(async () => {
  const initialized = await mixinApi
    .getVersion()
    .then((res) => res.data.initialized)
    .catch(() => false);

  if (!initialized) {
    return {
      redirect: {
        destination: '/setup',
        permanent: false,
      },
    };
  }

  return {
    props: {},
  };
});

const LoginPage: NextPage = () => {
  const { login } = useAuth();
  const { openPersistNotistack } = useNotistack();
  const formMethods = useForm<LoginForm>({
    defaultValues: generateProperty(loginFormJtd),
  });
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = formMethods;
  const [isError, setIsError] = useState<boolean>(false);
  const router = useRouter();

  const handleLogin = async (data: LoginForm) => {
    setIsError(false);
    const { error } = await login(data.username, data.password);
    if (!error) {
      router.push('/');
      return;
    }
    setIsError(true);
    openPersistNotistack('Login failed.', { variant: 'error' });
  };

  return (
    <NoAuthLayout>
      <Head>
        <title>Virty - Login</title>
      </Head>

      <Card elevation={0} sx={{ width: 500, margin: 'auto' }}>
        <CardHeader title="Login" />
        <CardContent component={'form'} onSubmit={handleSubmit(handleLogin)}>
          <FormProvider {...formMethods}>
            <JtdForm rootJtd={loginFormJtd} isEditing isError={isError} />
          </FormProvider>
          <Grid container justifyContent="flex-end">
            <LoadingButton type="submit" variant="contained" disableElevation loading={isSubmitting}>
              Login
            </LoadingButton>
          </Grid>
        </CardContent>
      </Card>
    </NoAuthLayout>
  );
};

export default LoginPage;

const loginFormJtd = {
  metadata: {
    spread: true,
  },
  properties: {
    username: {
      metadata: {
        name: 'Username',
        default: '',
      },
      type: 'string',
    },
    password: {
      metadata: {
        name: 'Password',
        default: '',
        customType: 'password',
      },
      type: 'string',
    },
  },
} as const;
