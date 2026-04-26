import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type CityGlbDownloadState = {
  modelIdsByLayout: Record<string, string[]>;
};

const initialState: CityGlbDownloadState = {
  modelIdsByLayout: {},
};

const cityGlbDownloadSlice = createSlice({
  name: "cityGlbDownload",
  initialState,
  reducers: {
    setLayoutCityGlbModelIds(
      state,
      action: PayloadAction<{ layoutId: string; modelIds: string[] }>
    ) {
      const { layoutId, modelIds } = action.payload;
      if (!layoutId) return;
      state.modelIdsByLayout[layoutId] = Array.from(new Set(modelIds.filter(Boolean)));
    },
    clearLayoutCityGlbModelIds(state, action: PayloadAction<string>) {
      const layoutId = action.payload;
      if (!layoutId) return;
      state.modelIdsByLayout[layoutId] = [];
    },
  },
});

export const { setLayoutCityGlbModelIds, clearLayoutCityGlbModelIds } = cityGlbDownloadSlice.actions;
export default cityGlbDownloadSlice.reducer;