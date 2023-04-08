import { LoadingButton } from '@mui/lab';
import { Box, Divider, Drawer, IconButton, Toolbar, Typography, useTheme } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { Schema } from 'jtd';
import { FilterSettings } from 'mdi-material-ui';
import { useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { generateProperty } from '~/lib/jtd';
import { Choice, MetaData } from '~/lib/jtd/types';
import { closedMixin, openedMixin } from '~/lib/utils/drawer';
import { useDrawer } from '~/store/drawerState';
import { useChoicesFetchers } from '~/store/formState';

const DRAWER_WIDTH = 350;

type JtdSchema = Schema & { metadata?: MetaData };

type Props<F> = {
  filtersJtd: F;
  choicesFetchers?: Record<string, () => Promise<Choice[]>>;
  submitLoading?: boolean;
  onSubmit: (filters: JTDDataType<F>) => void;
};

type FilterSettingsDrawerComponent = {
  <F = JtdSchema>(props: Props<F>): JSX.Element;
};

export const FilterSettingsDrawer: FilterSettingsDrawerComponent = ({
  filtersJtd,
  choicesFetchers,
  submitLoading,
  onSubmit,
}) => {
  const { rightDrawer, setRightDrawer, toggleRightDrawer, setRightDrawerOptions, resetRightDrawer } = useDrawer();
  const theme = useTheme();
  const formMethods = useForm({
    defaultValues: generateProperty(filtersJtd as JtdSchema),
  });
  const { handleSubmit } = formMethods;
  const { setFetcher, reset: resetFetchers } = useChoicesFetchers();

  useEffect(() => {
    setRightDrawerOptions({
      enable: true,
      openedWidth: `${DRAWER_WIDTH}px`,
      closedWidth: `calc(${theme.spacing(9)} + 1px)`,
    });
    return () => {
      resetRightDrawer();
    };
  }, [setRightDrawerOptions, resetRightDrawer, theme]);

  useEffect(() => {
    if (!choicesFetchers) {
      return;
    }
    resetFetchers();
    Object.entries(choicesFetchers).forEach(([key, fetcher]) => {
      setFetcher(key, fetcher);
    });
  }, [choicesFetchers, setFetcher, resetFetchers]);

  return (
    <Drawer
      open={rightDrawer}
      onClose={() => setRightDrawer(false)}
      variant="permanent"
      anchor="right"
      sx={
        rightDrawer
          ? {
              ...openedMixin(theme),
              '& .MuiDrawer-paper': openedMixin(theme, DRAWER_WIDTH),
            }
          : {
              ...closedMixin(theme),
              '& .MuiDrawer-paper': closedMixin(theme),
              '& span': {
                opacity: 0,
              },
            }
      }
    >
      <Toolbar />
      <Box display="flex" alignItems="center" sx={{ px: 2, py: 2 }}>
        <Typography
          variant="h6"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          Filter Settings
        </Typography>
        <IconButton onClick={toggleRightDrawer} sx={{ ml: 'auto' }}>
          <FilterSettings />
        </IconButton>
      </Box>
      <Divider />
      <FormProvider {...formMethods}>
        <JtdForm rootJtd={filtersJtd as JtdSchema} isEditing={true} />
      </FormProvider>
      <LoadingButton
        onClick={handleSubmit(onSubmit)}
        variant="contained"
        disableElevation
        loading={submitLoading}
        sx={{ mx: 2 }}
      >
        Search
      </LoadingButton>
    </Drawer>
  );
};
