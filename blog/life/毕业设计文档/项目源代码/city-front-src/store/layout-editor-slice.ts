import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type LayoutEditorState = {
  layoutId: string | null;
  svgContent: string;
  svgUrl: string;
  isEditorOpen: boolean;
  editingLayoutId: string | null;
  editingSvgContent: string;
};

const initialState: LayoutEditorState = {
  layoutId: null,
  svgContent: "",
  svgUrl: "",
  isEditorOpen: false,
  editingLayoutId: null,
  editingSvgContent: "",
};

const layoutEditorSlice = createSlice({
  name: "layoutEditor",
  initialState,
  reducers: {
    setLayoutId(state, action: PayloadAction<string | null>) {
      state.layoutId = action.payload;
    },
    setSvgContent(state, action: PayloadAction<string>) {
      state.svgContent = action.payload;
    },
    setSvgUrl(state, action: PayloadAction<string>) {
      state.svgUrl = action.payload;
    },
    setEditingLayoutId(state, action: PayloadAction<string | null>) {
      state.editingLayoutId = action.payload;
    },
    openEditor(state, action: PayloadAction<{ layoutId: string; svgContent: string }>) {
      state.isEditorOpen = true;
      state.editingLayoutId = action.payload.layoutId;
      state.editingSvgContent = action.payload.svgContent;
    },
    closeEditor(state) {
      state.isEditorOpen = false;
    },
    setEditingSvgContent(state, action: PayloadAction<string>) {
      state.editingSvgContent = action.payload;
    },
    applyEditedSvgContent(state) {
      state.svgContent = state.editingSvgContent;
      state.isEditorOpen = false;
    },
    resetEditorState(state) {
      state.isEditorOpen = false;
      state.editingLayoutId = null;
      state.editingSvgContent = "";
    },
  },
});

export const {
  setLayoutId,
  setSvgContent,
  setSvgUrl,
  setEditingLayoutId,
  openEditor,
  closeEditor,
  setEditingSvgContent,
  applyEditedSvgContent,
  resetEditorState,
} = layoutEditorSlice.actions;

export default layoutEditorSlice.reducer;
