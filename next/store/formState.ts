import { Schema } from 'jtd';
import { useCallback, useEffect, useState } from 'react';
import { FieldValues, UseFormGetValues } from 'react-hook-form';
import { atom, DefaultValue, selectorFamily, useRecoilState, useResetRecoilState, useSetRecoilState } from 'recoil';
import { ajv, getRelatedValue } from '~/lib/jtd';
import { Choice, MetaData } from '~/lib/jtd/types';

type ChoicesFetcher = {
  exec: () => Promise<Choice[]>;
  cache?: Choice[];
};

const choicesFetchersState = atom<Map<string, ChoicesFetcher>>({
  key: 'choicesFetchers',
  default: new Map(),
});

export const useChoicesFetchers = () => {
  const setChoicesFetchers = useSetRecoilState(choicesFetchersState);
  const reset = useResetRecoilState(choicesFetchersState);

  const setFetcher = useCallback(
    (
      name: string,
      fetcherFunction?: ChoicesFetcher['exec'] | undefined,
      options?: {
        useCache?: boolean;
      }
    ) => {
      setChoicesFetchers((oldValue) => {
        if (options?.useCache) {
          const oldValueEntry = oldValue.get(name);
          if (oldValueEntry) {
            return oldValue;
          }
        }
        const newValue = new Map(oldValue);
        if (!fetcherFunction) {
          newValue.delete(name);
        } else {
          newValue.set(name, {
            exec: fetcherFunction,
          });
        }
        return newValue;
      });
    },
    [setChoicesFetchers]
  );

  return { setFetcher, reset };
};

const choicesFetcherSelector = selectorFamily<ChoicesFetcher | undefined, string>({
  key: 'choicesFetcher',
  get:
    (name) =>
    ({ get }) =>
      get(choicesFetchersState).get(name),
  set:
    (name) =>
    ({ set }, newFetcher?: ChoicesFetcher | DefaultValue | ChoicesFetcher['exec']) => {
      set(choicesFetchersState, (oldValue) => {
        const newValue = new Map(oldValue);
        if (!newFetcher || newFetcher instanceof DefaultValue) {
          newValue.delete(name);
        } else if (typeof newFetcher === 'function') {
          newValue.set(name, {
            exec: newFetcher,
          });
        } else {
          newValue.set(name, newFetcher);
        }
        return newValue;
      });
    },
});

export const useChoices = (
  metadata: MetaData | undefined,
  getValues: UseFormGetValues<FieldValues>,
  currentName: string
) => {
  const choicesName =
    typeof metadata?.choices === 'string'
      ? metadata.choices
      : typeof metadata?.choices === 'function'
      ? metadata.choices(getRelatedValue(getValues, currentName))
      : '';
  const [fetcher, setFetcher] = useRecoilState(choicesFetcherSelector(choicesName));
  const [choices, setChoices] = useState<Choice[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const getChoices = useCallback(async () => {
    if (!metadata?.choices) {
      return {
        data: null,
        error: new Error('Choices is not defined.'),
      };
    }
    if (Array.isArray(metadata.choices)) {
      return {
        data: metadata.choices,
        error: null,
      };
    }
    if (!fetcher) {
      return {
        data: null,
        error: new Error('Choices fetcher is not defined.'),
      };
    }
    if (fetcher.cache) {
      return {
        data: fetcher.cache,
        error: null,
      };
    }
    return fetcher
      .exec()
      .then((data) => {
        setFetcher((oldValue) => {
          if (!oldValue) {
            return undefined;
          }
          return {
            exec: oldValue.exec,
            cache: data,
          };
        });
        return {
          data,
          error: null,
        };
      })
      .catch((error) => ({
        data: null,
        error,
      }));
  }, [metadata, fetcher, setFetcher]);

  useEffect(() => {
    setIsLoading(true);
    getChoices().then(({ data }) => {
      if (data) {
        setChoices(data);
        setIsLoading(false);
      }
    });
  }, [getChoices]);

  return { choices, isLoading };
};

export const useJtdForm = (jtd: Schema) => {
  useEffect(() => {
    if (ajv.getSchema('JTD')) {
      return;
    }
    ajv.addSchema(jtd, 'JTD');
  }, [jtd]);

  const reset = useCallback(() => {
    ajv.removeSchema('JTD');
  }, []);

  return { reset };
};
