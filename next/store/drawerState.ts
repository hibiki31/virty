import { atom, useRecoilState } from 'recoil';

export const drawerState = atom<boolean>({
  key: 'drawer',
  default: true,
});

export const useDrawer = () => {
  const [drawer, setDrawer] = useRecoilState(drawerState);

  const openDrawer = () => setDrawer(true);
  const closeDrawer = () => setDrawer(false);
  const toggleDrawer = () => setDrawer(!drawer);

  return { drawer, openDrawer, closeDrawer, toggleDrawer };
};
