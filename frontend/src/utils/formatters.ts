import type { SeasonName } from '@/api/api-contract';

const seasonLabels: Readonly<Record<SeasonName, string>> = {
  winter: '冬季',
  spring: '春季',
  summer: '夏季',
  fall: '秋季',
};

const numberFormatter = new Intl.NumberFormat('zh-CN');

export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

export function formatApiDate(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (match === null) {
    return value;
  }

  const [, year, month, day] = match;
  return `${year}年${month}月${day}日`;
}

export function formatSeason(season: SeasonName): string {
  return seasonLabels[season];
}

export function formatOptionalNumber(value: number | null): string {
  return value === null ? '未知' : formatNumber(value);
}
