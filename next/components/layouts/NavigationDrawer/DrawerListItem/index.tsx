import {
  Box,
  Link,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Tooltip,
  useTheme,
} from '@mui/material';
import { ChevronRight } from 'mdi-material-ui';
import NextLink from 'next/link';
import { useRouter } from 'next/router';
import { FC, memo } from 'react';
import { DrawerItem } from '../config';

type Props = {
  item: DrawerItem;
  parentPath?: string;
};

export const DrawerListItem: FC<Props> = memo(function NotMemoDrawerListItem({ item, parentPath }) {
  const pathname = parentPath ? `${parentPath}${item.path}` : item.path;
  if (!item.children?.length) {
    return (
      <NextLink href={{ pathname }} passHref>
        <Link underline="none" color="inherit">
          <BaseDrawerListItem item={item} parentPath={parentPath} />
        </Link>
      </NextLink>
    );
  }

  return (
    <NextLink href={{ pathname }} passHref>
      <Tooltip
        title={
          <Paper elevation={4}>
            <List sx={{ py: 0.5 }}>
              {item.children.map((childItem, i) => (
                <DrawerListItem key={i} item={childItem} parentPath={item.path} />
              ))}
            </List>
          </Paper>
        }
        components={{ Tooltip: Paper }}
        componentsProps={{
          tooltip: {
            sx: {
              mt: '-4px',
            },
          },
          transition: {
            timeout: 0,
          },
        }}
        enterDelay={0}
        placement="right-start"
      >
        <Link underline="none" color="inherit">
          <BaseDrawerListItem item={item} parentPath={parentPath} />
        </Link>
      </Tooltip>
    </NextLink>
  );
});

const BaseDrawerListItem: FC<Props> = memo(function NotMemoBaseDrawerListItem({ item, parentPath }) {
  const theme = useTheme();
  const router = useRouter();
  const pathname = parentPath ? `${parentPath}${item.path}` : item.path;

  return (
    <ListItem
      dense
      disablePadding
      sx={{
        px: 1,
        py: 0.5,
        '> div': {
          borderRadius: 1,
        },
        '> .Mui-selected': {
          backgroundColor: `${theme.palette.action.selected} !important`,
        },
      }}
    >
      <ListItemButton selected={router.pathname === pathname}>
        {item.icon && <ListItemIcon>{item.icon}</ListItemIcon>}
        <ListItemText
          primary={
            !item.children?.length ? (
              item.title
            ) : (
              <Box display="flex" alignItems="center" justifyContent="space-between">
                {item.title}
                <ChevronRight fontSize="small" />
              </Box>
            )
          }
        />
      </ListItemButton>
    </ListItem>
  );
});
