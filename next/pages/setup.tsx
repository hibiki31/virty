import { LoadingButton } from '@mui/lab';
import { Card, CardActions, CardContent, CardHeader, Grid, Typography } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import type { NextPage } from 'next';
import Head from 'next/head';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { NoAuthLayout } from '~/components/layouts/NoAuthLayout';
import { mixinApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { makeRequireLogoutProps } from '~/lib/utils/makeGetServerSideProps';

type FormData = JTDDataType<typeof formJtd>;

export const getServerSideProps = makeRequireLogoutProps(async () => {
  const initialized = await mixinApi
    .getVersionApiVersionGet()
    .then((res) => res.data.initialized)
    .catch(() => false);

  if (initialized) {
    return {
      redirect: {
        destination: '/login',
        permanent: false,
      },
    };
  }

  return {
    props: {},
  };
});

const Page: NextPage = () => {
  const formMethods = useForm<FormData>({
    defaultValues: generateProperty(formJtd),
  });
  const {
    handleSubmit,
    formState: { isSubmitting, isValid },
  } = formMethods;

  const handleSetup = (data: FormData) => {
    console.log('handleSetup', data);
  };

  return (
    <NoAuthLayout>
      <Head>
        <title>Virty - Setup</title>
      </Head>

      <Card elevation={0}>
        <CardHeader title="Setup" />
        <CardContent>
          <Typography variant="body2" marginBottom={3} sx={{ whiteSpace: 'pre-line' }}>
            {'Create an administrative user.\nThis will fail if a user with administrative privileges already exists.'}
          </Typography>
          <FormProvider {...formMethods}>
            <JtdForm rootJtd={formJtd} isEditing />
          </FormProvider>
        </CardContent>
        <CardActions>
          <Grid container justifyContent="flex-end">
            <Grid item>
              <LoadingButton
                onClick={handleSubmit(handleSetup)}
                variant="contained"
                disableElevation
                disabled={!isValid}
                loading={isSubmitting}
              >
                Setup
              </LoadingButton>
            </Grid>
          </Grid>
        </CardActions>
      </Card>
    </NoAuthLayout>
  );
};

export default Page;

const formJtd = {
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
