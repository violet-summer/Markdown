import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { LayoutEditorPage } from "./layout-editor";

describe("LayoutEditorPage", () => {
  it("renders the layout controls", () => {
    render(<LayoutEditorPage />);

    expect(screen.getByText("Layout Parameters")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate layout/i })).toBeInTheDocument();
  });

  it("loads the user layout list", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        code: 200,
        message: "OK",
        data: [{ layout_id: "1", svgUrl: "http://example.com/layout.svg", status: 2 }],
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<LayoutEditorPage />);

    await waitFor(() => {
      expect(screen.getByText("Layout #1")).toBeInTheDocument();
    });

    vi.unstubAllGlobals();
  });
});
