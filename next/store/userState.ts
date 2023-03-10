import { useRouter } from 'next/router';
import { parseCookies, setCookie } from 'nookies';
import { useEffect } from 'react';
import { atom, useRecoilState } from 'recoil';
import { authApi } from '~/lib/api';
import { SCOPE_TO_LABEL } from '~/lib/api/auth';

type Scope = keyof typeof SCOPE_TO_LABEL;

export type User = {
  username: string;
  scopes: Scope[];
  scopeIndex: number;
  isAdminMode: boolean;
};

type Payload = {
  sub: string;
  scopes: Scope[];
};

type UserState = User | null | undefined; // null = not logged in, undefined = loading

export const userState = atom<UserState>({
  key: 'user',
  default: undefined,
});

const getUserFromToken = (token: string): User => {
  const pyaload: Payload = JSON.parse(atob(token.split('.')[1]));
  const adminIndex = pyaload.scopes.findIndex((s) => s === 'admin');
  return {
    username: pyaload.sub,
    scopes: pyaload.scopes,
    scopeIndex: adminIndex > -1 ? adminIndex : 0,
    isAdminMode: adminIndex > -1,
  };
};

export const useGetUser = (): UserState => {
  const [user, setUser] = useRecoilState(userState);
  const { token } = parseCookies();

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    setUser(getUserFromToken(token));
  }, [token, setUser]);

  return user;
};

export const useAuth = () => {
  const [user, setUser] = useRecoilState(userState);
  const router = useRouter();

  const login = async (username: string, password: string) => {
    if (user) {
      console.log('User already logged in');
      return { user, error: null };
    }

    return authApi
      .loginForAccessTokenApiAuthPost(username, password)
      .then((res) => {
        const _user = getUserFromToken(res.data.access_token);
        setUser(_user);
        setCookie(null, 'token', res.data.access_token, {
          maxAge: 30 * 24 * 60 * 60,
          path: '/',
        });
        return {
          user: _user,
          error: null,
        };
      })
      .catch((err: Error) => ({ user: null, error: err }));
  };

  const logout = async () => {
    router.push('/logout');
  };

  const changeScope = (scopeIndex: number) => {
    if (!user) {
      console.log('User not logged in');
      return;
    }
    if (!user.scopes[scopeIndex]) {
      console.log('Invalid scope index');
      return;
    }
    setUser({ ...user, scopeIndex: scopeIndex, isAdminMode: user.scopes[scopeIndex] === 'admin' });
  };

  return { user, login, logout, changeScope };
};
