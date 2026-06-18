import React from 'react';
import { getProviderMeta } from '../utils/multicloud';

interface ProviderBadgeProps {
  provider: string;
}

export const ProviderBadge: React.FC<ProviderBadgeProps> = ({ provider }) => {
  const meta = getProviderMeta(provider);
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold ${meta.badgeClass}`}>
      {meta.label}
    </span>
  );
};
