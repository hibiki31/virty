import { Schema } from 'jtd';
import { useCallback, useEffect, useState } from 'react';
import { atom, useRecoilState, useResetRecoilState } from 'recoil';
import { ajv } from '~/lib/jtd';
import { Choice, MetaData } from '~/lib/jtd/types';

type TableChoicesState = {
  [key: string]: Choice[];
};

export const tableChoicesState = atom<TableChoicesState>({
  key: 'tableChoices',
  default: {},
});

export const useChoices = (metadata?: MetaData) => {
  const [tableChoices, setTableChoices] = useRecoilState(tableChoicesState);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetch = useCallback(async () => {
    if (!metadata?.choices) {
      return {
        data: null,
        error: new Error('Choices is not defined.'),
      };
    }
    if (Array.isArray(metadata.choices)) {
      setTableChoices((prev) => ({
        ...prev,
        [metadata.name]: metadata.choices as Choice[],
      }));
      return {
        data: metadata.choices,
        error: null,
      };
    }
    const cachedChoices = tableChoices[metadata.choices];
    if (cachedChoices) {
      return {
        data: cachedChoices,
        error: null,
      };
    }

    const { data, error } = await fetchChoices(metadata.choices);
    if (error) {
      return {
        data: null,
        error,
      };
    }
    setTableChoices((prev) => ({
      ...prev,
      [metadata.choices as string]: data,
    }));
    return {
      data,
      error: null,
    };
  }, [metadata, tableChoices, setTableChoices]);

  useEffect(() => {
    fetch()
      .then(({ data, error }) => {
        if (error) {
          if (error.message !== 'Choices is not defined.') {
            console.error(error);
          }
          return;
        }
        setChoices(data);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [fetch]);

  return { choices, isLoading, fetch };
};

export const useJtdForm = (jtd: Schema) => {
  const resetTableChoices = useResetRecoilState(tableChoicesState);

  useEffect(() => {
    if (ajv.getSchema('JTD')) {
      return;
    }
    ajv.addSchema(jtd, 'JTD');
  }, [jtd]);

  const reset = useCallback(() => {
    ajv.removeSchema('JTD');
    resetTableChoices();
  }, [resetTableChoices]);

  return { reset };
};

const fetchChoices = async (tableName: string): Promise<any> => {
  switch (tableName) {
  }
};
