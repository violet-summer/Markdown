import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModelViewerPage } from "./model-viewer";

describe("ModelViewerPage", () => {
  it("renders the generate model controls", () => {
    render(<ModelViewerPage />);

    expect(screen.getByText("Generate Model")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate model/i })).toBeInTheDocument();
  });

  it("loads the user model list", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        code: 200,
        message: "OK",
        data: [
          {
            modelId: "4",
            layout_id: "2",
            objUrl: "http://example.com/model.obj",
            mtlUrl: "http://example.com/model.mtl",
            status: 1,
          },
        ],
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ModelViewerPage />);

    await waitFor(() => {
      expect(screen.getByText("Model #4")).toBeInTheDocument();
    });

    vi.unstubAllGlobals();
  });
});
