import dayjs from 'dayjs';

export const formatDate = (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss');
