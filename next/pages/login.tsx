import { LoadingButton } from '@mui/lab';
import { Button, Card, CardContent, CardHeader, Grid } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import type { NextPage } from 'next';
import Head from 'next/head';
import { useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { generateProperty } from '~/lib/jtd';
import { makeRequireLogoutProps } from '~/lib/utils/makeGetServerSideProps';
import { useAuth } from '~/store/userState';

type LoginForm = JTDDataType<typeof loginFormJtd>;

export const getServerSideProps = makeRequireLogoutProps();

const LoginPage: NextPage = () => {
  const { user, login, logout } = useAuth();
  const formMethods = useForm<LoginForm>({
    defaultValues: generateProperty(loginFormJtd),
  });
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = formMethods;
  const [isError, setIsError] = useState<boolean>(false);

  const handleLogin = async (data: LoginForm) => {
    setIsError(false);
    const { error } = await login(data.username, data.password);
    if (error) {
      console.log(error);
      setIsError(true);
    }
  };

  return (
    <>
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

      <Button variant="contained" onClick={logout}>
        Logout
      </Button>
      {user && <div>{JSON.stringify(user)}</div>}
    </>
  );
};

export default LoginPage;

const loginFormJtd = {
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
