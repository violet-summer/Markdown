import { useAppDispatch, useAppSelector } from "@/store/hooks";
import {
  setEditingLayoutId,
  setLayoutId,
  setSvgContent,
  setSvgUrl,
} from "@/store/layout-editor-slice";

export function useLayoutEditorStore() {
  const dispatch = useAppDispatch();

  const layoutId = useAppSelector((state) => state.layoutEditor.layoutId);
  const svgContent = useAppSelector((state) => state.layoutEditor.svgContent);
  const svgUrl = useAppSelector((state) => state.layoutEditor.svgUrl);
  const editingLayoutId = useAppSelector((state) => state.layoutEditor.editingLayoutId);

  return {
    layoutId,
    svgContent,
    svgUrl,
    editingLayoutId,
    setLayoutId: (next: string | null) => dispatch(setLayoutId(next)),
    setSvgContent: (next: string) => dispatch(setSvgContent(next)),
    setSvgUrl: (next: string) => dispatch(setSvgUrl(next)),
    setEditingLayoutId: (next: string | null) => dispatch(setEditingLayoutId(next)),
  };
}
