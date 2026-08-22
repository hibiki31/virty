type PaginatedQuery = {
  page?: number | null;
};

/**
 * UIの1始まりpageをAPIの0始まりpageへ変換し、呼び出し元のqueryは変更しない。
 */
export function toApiPageQuery<T extends PaginatedQuery>(query: T): T {
  const uiPage = query.page ?? 1;

  return {
    ...query,
    page: Math.max(0, uiPage - 1),
  };
}
