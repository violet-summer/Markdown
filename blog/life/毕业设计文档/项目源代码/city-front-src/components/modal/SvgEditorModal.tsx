import { useEffect, useState } from "react";
import { SvgVisualEditor } from "../svg/SvgVisualEditor";
import { closeEditor, setEditingSvgContent } from "@/store/layout-editor-slice";
import { useAppDispatch, useAppSelector } from "@/store/hooks";

type SvgEditorModalProps = {
  onSave: (svg_content: string) => void;
  onGenerateModel: () => void;
};

export function SvgEditorModal({
  onSave,
  onGenerateModel,
}: SvgEditorModalProps) {
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector((state) => state.layoutEditor.isEditorOpen);
  const layout_id = useAppSelector((state) => state.layoutEditor.editingLayoutId) ?? "";
  const svg_content = useAppSelector((state) => state.layoutEditor.editingSvgContent);
  const [editedSvg, setEditedSvg] = useState(svg_content);
  const [hasChanges, setHasChanges] = useState(false);
  const [layoutParams, setLayoutParams] = useState<Record<string, any>>({});

  useEffect(() => {
    setEditedSvg(svg_content);
    setHasChanges(false);
    // 从localStorage获取对应layout的params
    try {
      const stored = localStorage.getItem(`layout_params_${layout_id}`);
      if (stored) {
        setLayoutParams(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Failed to load layout params:", e);
    }
  }, [svg_content, isOpen, layout_id]);

  const handleSvgChange = (newsvg_content: string) => {
    setEditedSvg(newsvg_content);
    dispatch(setEditingSvgContent(newsvg_content));
    setHasChanges(true);
  };

  const handleSave = () => {
    onSave(editedSvg);
    setHasChanges(false);
  };

  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-white";
  const buttonSuccess = "border-transparent bg-[var(--accent-2)] text-white";
  const buttonGhost = "bg-transparent text-[var(--ink)]";
  const modalOverlay = "fixed inset-0 z-50 grid place-items-center bg-black/40 p-4";
  const modalContent = "w-full max-w-[1100px] overflow-hidden rounded-[16px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_18px_40px_-24px_var(--shadow)]";
  const modalHeader = "flex items-center justify-between gap-3 border-b border-[var(--border)] bg-[var(--surface-2)] px-4 py-2";
  const modalTitle = "m-0 text-[15px] font-semibold";
  const modalClose = "grid h-8 w-8 place-items-center rounded-full border border-[var(--border)] bg-[var(--surface)] text-[16px] text-[var(--muted)]";
  const modalBody = "p-4";
  const modalFooter = "flex flex-wrap items-center justify-end gap-2 border-t border-[var(--border)] bg-[var(--surface-2)] px-4 py-2";

  const handleClose = () => {
    if (hasChanges) {
      if (confirm("有未保存的更改，确定要关闭吗？")) {
        dispatch(closeEditor());
      }
    } else {
      dispatch(closeEditor());
    }
  };

  // 从params获取世界维度，用于调整编辑器尺寸
  const worldDims = layoutParams?.world_dimensions || { x: 640, z: 360 };
  const editorWidth = Math.min(900, Math.max(600, worldDims.x * 1.4));
  const editorHeight = Math.min(700, Math.max(450, worldDims.z * 1.4));

  if (!isOpen) return null;

  return (
    <div className={modalOverlay} onClick={handleClose}>
      <div className={modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={modalHeader}>
          <h2 className={modalTitle}>可视化SVG编辑器 - 布局 #{layout_id}</h2>
          <button className={modalClose} onClick={handleClose}>
            ×
          </button>
        </div>

        <div className={modalBody}>
          <SvgVisualEditor
            svg_content={editedSvg}
            onChange={handleSvgChange}
            width={editorWidth}
            height={editorHeight}
          />
        </div>

        <div className={modalFooter}>
          <button
            className={`${buttonBase} ${buttonSuccess}`}
            onClick={onGenerateModel}
            title="使用当前SVG生成3D模型"
          >
            🏗️ 生成3D模型
          </button>
          <button
            className={`${buttonBase} ${buttonPrimary}`}
            onClick={handleSave}
            disabled={!hasChanges}
          >
            💾 保存更改
          </button>
          <button className={`${buttonBase} ${buttonGhost}`} onClick={handleClose}>
            取消
          </button>
        </div>
      </div>
    </div>
  );
}
