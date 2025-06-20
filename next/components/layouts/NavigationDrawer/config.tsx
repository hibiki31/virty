import {
  CubeOutline,
  CheckboxMultipleMarkedOutline,
  Server,
  Wan,
  Database,
  Harddisk,
  TagMultiple,
  Account,
  FolderStar,
  ViewDashboard,
} from 'mdi-material-ui';

export type DrawerItem = {
  title: string;
  path: string;
  icon?: JSX.Element;
  children?: DrawerItem[];
};

export const DRAWER_ITEMS: DrawerItem[] = [
  {
    title: 'Dashboard',
    path: '/',
    icon: <ViewDashboard />,
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
  },
  {
    title: 'Networks',
    path: '/networks',
    icon: <Wan />,
    children: [
      {
        title: 'Networks',
        path: '',
      },
      {
        title: 'Network Pools',
        path: '/pools',
      },
    ],
  },
  {
    title: 'Storages',
    path: '/storages',
    icon: <Database />,
    children: [
      {
        title: 'Storages',
        path: '',
      },
      {
        title: 'Storage Pools',
        path: '/pools',
      },
    ],
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
