import React from 'react';

export const isDev = typeof import.meta !== 'undefined' && Boolean((import.meta as any).env?.DEV);

export function devAttrs(name?: string, layer?: string): Record<string, string> {
  if (!isDev) return {};
  const attrs: Record<string, string> = {};
  if (name) attrs['data-component'] = name;
  if (layer) attrs['data-layer'] = layer;
  return attrs;
}

export function DevSvgTitle({ name }: { name: string }) {
  if (!isDev) return null;
  return <title>{name}</title>;
}

export function withDevName<P extends Record<string, any>>(Component: React.ComponentType<P>, name: string): React.ComponentType<P> {
  if (!isDev) return Component;
  const Wrapped: React.FC<P> = (props) => (
    <div data-component={name} style={{ display: 'contents' }}>
      <Component {...props} />
    </div>
  );
  Wrapped.displayName = `DevNamed(${name})`;
  return Wrapped;
}

