import { useRouter } from 'next/router';
import { destroyCookie, parseCookies, setCookie } from 'nookies';
import { useEffect } from 'react';
import { atom, useRecoilState } from 'recoil';
import { authApi } from '~/lib/api';

export type Scope = 'user' | 'admin';

export type User = {
  username: string;
  scopes: Scope[];
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

const getUserFromToken = (token: string) => {
  const pyaload: Payload = JSON.parse(atob(token.split('.')[1]));
  return {
    username: pyaload.sub,
    scopes: pyaload.scopes,
  };
};

export const useGetUser = (): UserState => {
  const [user, setUser] = useRecoilState(userState);

  useEffect(() => {
    const { token } = parseCookies();
    if (!token) {
      setUser(null);
      return;
    }
    setUser(getUserFromToken(token));
  }, [setUser]);

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
    setUser(null);
    destroyCookie(null, 'token');
    router.push('/login');
  };

  return { user, login, logout };
};
