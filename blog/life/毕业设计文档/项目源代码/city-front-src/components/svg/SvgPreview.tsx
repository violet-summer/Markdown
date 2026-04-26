type SvgPreviewProps = {
  svg_content?: string;
  svgUrl?: string;
};

import React, { useEffect, useState } from "react";
import { useAppSelector } from "@/store/hooks";

export function SvgPreview({ svg_content, svgUrl }: SvgPreviewProps) {
  const storeSvgContent = useAppSelector((state) => state.layoutEditor.svgContent);
  const storeSvgUrl = useAppSelector((state) => state.layoutEditor.svgUrl);
  const resolvedSvgContent = svg_content ?? storeSvgContent;
  const resolvedSvgUrl = svgUrl ?? storeSvgUrl;
  const [fetchedSvg, setFetchedSvg] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!resolvedSvgContent && resolvedSvgUrl) {
      setLoading(true);
      setError("");
      setFetchedSvg("");
      fetch(resolvedSvgUrl)
        .then(async (res) => {
          if (!res.ok) throw new Error("SVG 加载失败");
          const text = await res.text();
          setFetchedSvg(text);
        })
        .catch((e) => setError(e.message || "SVG 加载失败"))
        .finally(() => setLoading(false));
    } else {
      setFetchedSvg("");
      setError("");
      setLoading(false);
    }
  }, [resolvedSvgContent, resolvedSvgUrl]);

  const svgToRender = resolvedSvgContent || fetchedSvg;


  if (!svgToRender && !resolvedSvgUrl) {
    return (
      <div className="flex flex-1 h-full min-h-0 items-center justify-center rounded-[10px] border border-dashed border-[var(--border)] bg-[var(--surface-2)] p-6 text-center text-[12px] text-[var(--muted)]">
        尚未加载 SVG。
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-1 h-full min-h-0 items-center justify-center rounded-[10px] border border-dashed border-[var(--border)] bg-[var(--surface-2)] p-6 text-center text-[12px] text-[var(--muted)]">
        SVG 加载中...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-1 h-full min-h-0 items-center justify-center rounded-[10px] border border-dashed border-[var(--border)] bg-[var(--surface-2)] p-6 text-center text-[12px] text-[var(--error)]">
        {error}
      </div>
    );
  }


  if (svgToRender) {
    // 自动为SVG标签加上自适应样式，防止被拉伸
    let safeSvg = svgToRender;
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(svgToRender, "image/svg+xml");
      const svgEl = doc.querySelector("svg");
      if (svgEl) {
        const viewBox = svgEl.getAttribute("viewBox");
        const rawWidth = Number.parseFloat(svgEl.getAttribute("width") || "");
        const rawHeight = Number.parseFloat(svgEl.getAttribute("height") || "");
        if (!viewBox && Number.isFinite(rawWidth) && Number.isFinite(rawHeight) && rawWidth > 0 && rawHeight > 0) {
          svgEl.setAttribute("viewBox", `0 0 ${rawWidth} ${rawHeight}`);
        }

        svgEl.removeAttribute("width");
        svgEl.removeAttribute("height");

        // 让SVG在容器内按比例尽量放大，最长边贴合，避免单边溢出
        svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");
        svgEl.setAttribute("style", "width:100%;height:100%;display:block;margin:auto;max-width:100%;max-height:100%;overflow:hidden;");
        safeSvg = svgEl.outerHTML;
      }
    } catch {}
    return (
      <div className="relative flex flex-1 min-w-0 h-full min-h-0 items-center justify-center rounded-[10px] border border-dashed border-[var(--border)] bg-[var(--surface-2)] p-3 overflow-hidden">
        <div
          dangerouslySetInnerHTML={{ __html: safeSvg }}
          className="absolute inset-0 m-auto flex h-[90%] w-[90%] min-h-0 min-w-0 max-h-full max-w-full items-center justify-center overflow-hidden"
        />
      </div>
    );
  }

  // 理论不会走到这里
  return null;
}
