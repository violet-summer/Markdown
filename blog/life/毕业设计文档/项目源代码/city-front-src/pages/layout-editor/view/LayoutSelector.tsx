import type { LayoutsListItem } from "@/models/layout-api";

type LayoutSelectorProps = {
  value: string;
  layouts: LayoutsListItem[];
  emptyLabel: string;
  optionPrefix: string;
  className?: string;
  selectClassName?: string;
  onChange: (value: string) => void;
};

export function LayoutSelector({
  value,
  layouts,
  emptyLabel,
  optionPrefix,
  className,
  selectClassName,
  onChange,
}: LayoutSelectorProps) {
  return (
    <label className={className}>
      <select className={selectClassName} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">{emptyLabel}</option>
        {layouts.map((layout) => (
          <option key={layout.layout_id} value={layout.layout_id}>
            {optionPrefix} {layout.layout_id}
          </option>
        ))}
      </select>
    </label>
  );
}
