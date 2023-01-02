import { Schema } from 'jtd';
import { useCallback, useEffect, useState } from 'react';
import { atom, DefaultValue, selectorFamily, useRecoilValue, useResetRecoilState, useSetRecoilState } from 'recoil';
import { ajv } from '~/lib/jtd';
import { Choice, MetaData } from '~/lib/jtd/types';

type ChoicesFetcher = () => Promise<Choice[]>;

type ChoicesFetchersState = {
  [key: string]: ChoicesFetcher;
};

const choicesFetchersState = atom<ChoicesFetchersState>({
  key: 'choicesFetchers',
  default: {},
});

const choicesFetcherSelector = selectorFamily<ChoicesFetcher, string>({
  key: 'choicesFetcher',
  get:
    (name) =>
    ({ get }) =>
      get(choicesFetchersState)[name],
  set:
    (name) =>
    ({ set }, newFetcher?: ChoicesFetcher | DefaultValue) => {
      set(choicesFetchersState, (oldValue) => {
        if (!newFetcher || newFetcher instanceof DefaultValue) {
          const { [name]: _, ...newValue } = oldValue;
          return newValue;
        }
        return {
          ...oldValue,
          [name]: newFetcher,
        };
      });
    },
});

export const useChoicesFetcher = (name: string) => {
  return useSetRecoilState(choicesFetcherSelector(name));
};

export const useChoices = (metadata?: MetaData) => {
  const fetcher = useRecoilValue(choicesFetcherSelector(typeof metadata?.choices === 'string' ? metadata.choices : ''));
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
    return fetcher()
      .then((data) => ({
        data,
        error: null,
      }))
      .catch((error) => ({
        data: null,
        error,
      }));
  }, [metadata, fetcher]);

  useEffect(() => {
    setIsLoading(true);
    getChoices().then(({ data }) => {
      if (data) {
        setChoices(data);
        setIsLoading(false);
      }
    });
  }, [getChoices]);

  return { choices: choices, isLoading };
};

export const useJtdForm = (jtd: Schema) => {
  const resetFetchers = useResetRecoilState(choicesFetchersState);

  useEffect(() => {
    if (ajv.getSchema('JTD')) {
      return;
    }
    ajv.addSchema(jtd, 'JTD');
  }, [jtd]);

  const reset = () => {
    ajv.removeSchema('JTD');
    resetFetchers();
  };

  return { reset };
};
