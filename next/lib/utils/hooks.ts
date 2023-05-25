import { useCallback, useState } from 'react';

export const usePagination = (defaultPage = 0, defaultLimit = 25) => {
  const [page, setPage] = useState(defaultPage);
  const [limit, setLimit] = useState(defaultLimit);

  const onPageChange = useCallback((page: number) => {
    setPage(page);
  }, []);

  const onLimitChange = useCallback((limit: number) => {
    setLimit(limit);
  }, []);

  return {
    page,
    limit,
    onPageChange,
    onLimitChange,
  };
};
