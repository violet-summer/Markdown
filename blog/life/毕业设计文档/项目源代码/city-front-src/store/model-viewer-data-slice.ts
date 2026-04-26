import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { LayoutWithModels } from "@/models/model-api";

export type ModelFileRecord = {
  model_id?: string;
  presigned_url?: string;
  objContent?: string;
  [property: string]: any;
};

type ModelViewerDataState = {
  layoutWithModels: LayoutWithModels[];
  modelFilesById: Record<string, ModelFileRecord>;
};

const initialState: ModelViewerDataState = {
  layoutWithModels: [],
  modelFilesById: {},
};

const modelViewerDataSlice = createSlice({
  name: "modelViewerData",
  initialState,
  reducers: {
    setLayoutWithModels(state, action: PayloadAction<LayoutWithModels[]>) {
      state.layoutWithModels = action.payload;
    },
    setModelFileById(
      state,
      action: PayloadAction<{ modelId: string; file: ModelFileRecord }>
    ) {
      const { modelId, file } = action.payload;
      if (!modelId) return;
      state.modelFilesById[modelId] = file;
    },
  },
});

export const { setLayoutWithModels, setModelFileById } = modelViewerDataSlice.actions;
export default modelViewerDataSlice.reducer;