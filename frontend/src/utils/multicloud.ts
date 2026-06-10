export type ProviderKey = 'AWS' | 'AZURE' | 'GCP';

interface ProviderMeta {
  key: ProviderKey;
  label: string;
  badgeClass: string;
  services: string[];
}

const PROVIDER_META: Record<ProviderKey, ProviderMeta> = {
  AWS: {
    key: 'AWS',
    label: 'AWS',
    badgeClass: 'bg-amber-100 text-amber-800',
    services: ['EC2', 'RDS', 'S3'],
  },
  AZURE: {
    key: 'AZURE',
    label: 'Azure',
    badgeClass: 'bg-blue-100 text-blue-800',
    services: ['Virtual Machines', 'Azure SQL', 'Blob Storage'],
  },
  GCP: {
    key: 'GCP',
    label: 'GCP',
    badgeClass: 'bg-green-100 text-green-800',
    services: ['Compute Engine', 'Cloud SQL', 'Cloud Storage'],
  },
};

const PROVIDER_MULTIPLIER: Record<ProviderKey, number> = {
  AWS: 1,
  AZURE: 0.93,
  GCP: 0.88,
};

export const normalizeProvider = (value?: string): ProviderKey => {
  const normalized = (value || '').toUpperCase();
  if (normalized.includes('AZURE')) return 'AZURE';
  if (normalized.includes('GCP') || normalized.includes('GOOGLE')) return 'GCP';
  return 'AWS';
};

export const getProviderMeta = (value?: string): ProviderMeta => {
  const provider = normalizeProvider(value);
  return PROVIDER_META[provider];
};

export const getProviderMultiplier = (value?: string): number => {
  const provider = normalizeProvider(value);
  return PROVIDER_MULTIPLIER[provider];
};

export const formatRelativeTime = (timestamp?: string | number | Date | null): string => {
  if (!timestamp) return 'Last synced just now';

  const time = new Date(timestamp).getTime();
  if (Number.isNaN(time)) return 'Last synced just now';

  const diffSeconds = Math.max(0, Math.floor((Date.now() - time) / 1000));
  if (diffSeconds < 30) return 'Last synced just now';
  if (diffSeconds < 60) return `Last synced ${diffSeconds}s ago`;

  const minutes = Math.floor(diffSeconds / 60);
  if (minutes < 60) return `Last synced ${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `Last synced ${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `Last synced ${days}d ago`;
};
