import { configureStore } from "@reduxjs/toolkit";
import layoutEditorReducer from "@/store/layout-editor-slice";
import cityGlbDownloadReducer from "@/store/city-glb-download-slice";
import modelViewerDataReducer from "@/store/model-viewer-data-slice";

export const store = configureStore({
  reducer: {
    layoutEditor: layoutEditorReducer,
    cityGlbDownload: cityGlbDownloadReducer,
    modelViewerData: modelViewerDataReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
