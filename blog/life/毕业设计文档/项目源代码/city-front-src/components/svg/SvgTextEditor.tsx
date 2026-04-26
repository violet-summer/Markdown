import { useState } from "react";
import { setSvgContent } from "@/store/layout-editor-slice";
import { useAppDispatch, useAppSelector } from "@/store/hooks";

type SvgTextEditorProps = {
  value?: string;
  onChange?: (value: string) => void;
  svgUrl?: string;
};

export function SvgTextEditor({ value, onChange, svgUrl }: SvgTextEditorProps) {
  const dispatch = useAppDispatch();
  const storeValue = useAppSelector((state) => state.layoutEditor.svgContent);
  const storeSvgUrl = useAppSelector((state) => state.layoutEditor.svgUrl);
  const resolvedValue = value ?? storeValue;
  const resolvedSvgUrl = svgUrl ?? storeSvgUrl;
  const [loading, setLoading] = useState(false);
  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";

  const applyChange = (nextValue: string) => {
    if (onChange) {
      onChange(nextValue);
      return;
    }
    dispatch(setSvgContent(nextValue));
  };

  const loadFromUrl = async () => {
    if (!resolvedSvgUrl) {
      return;
    }
    try {
      setLoading(true);
      const response = await fetch(resolvedSvgUrl);
      if (!response.ok) {
        throw new Error("加载 SVG 失败。");
      }
      const content = await response.text();
      applyChange(content);
    } catch (err) {
      applyChange("<!-- 无法加载 SVG 内容 -->");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-3 h-full min-h-0">
      <div className="flex flex-wrap gap-3">
        <button className={buttonBase} onClick={loadFromUrl} disabled={!resolvedSvgUrl || loading}>
          {loading ? "加载中..." : "从链接加载"}
        </button>
      </div>
      <textarea
        className="flex-1 min-h-0 w-full resize-none rounded-lg border border-[var(--border)] bg-[var(--surface)] p-2.5 text-[13px] text-[var(--ink)] font-['Courier_New',Courier,monospace]"
        value={resolvedValue}
        onChange={(event) => applyChange(event.target.value)}
        placeholder="在这里编辑 SVG 内容"
      />
    </div>
  );
}
