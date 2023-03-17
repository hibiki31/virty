import {
  Home,
  CubeOutline,
  CheckboxMultipleMarkedOutline,
  Server,
  Wan,
  Database,
  Harddisk,
  TagMultiple,
  Account,
  FolderStar,
} from 'mdi-material-ui';

export type DrawerItem = {
  title: string;
  path: string;
  icon?: JSX.Element;
  children?: DrawerItem[];
};

export const DRAWER_WIDTH = 250;

export const DRAWER_ITEMS: DrawerItem[] = [
  {
    title: 'Home',
    path: '/',
    icon: <Home />,
  },
  {
    title: 'VMs',
    path: '/vms',
    icon: <CubeOutline />,
  },
  {
    title: 'Nodes',
    path: '/nodes',
    icon: <Server />,
    children: [
      {
        title: 'Nodes',
        path: '',
      },
      {
        title: 'Node Pools',
        path: '/pools',
      },
    ],
  },
  {
    title: 'Networks',
    path: '/networks',
    icon: <Wan />,
  },
  {
    title: 'Storages',
    path: '/storages',
    icon: <Database />,
  },
  {
    title: 'Images',
    path: '/images',
    icon: <Harddisk />,
  },
  {
    title: 'Flavors',
    path: '/flavors',
    icon: <TagMultiple />,
  },
  {
    title: 'Users',
    path: '/users',
    icon: <Account />,
  },
  {
    title: 'Projects',
    path: '/projects',
    icon: <FolderStar />,
  },
  {
    title: 'Tasks',
    path: '/tasks',
    icon: <CheckboxMultipleMarkedOutline />,
  },
];
