import dayjs from 'dayjs';

export const formatDate = (date: string | number) => dayjs(date).format('YYYY-MM-DD HH:mm:ss');
