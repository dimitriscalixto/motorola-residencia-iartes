import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import App from "../src/App";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => null,
      }))
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders main action button", () => {
    render(<App />);

    expect(screen.getByRole("button", { name: /iniciar varredura da comunidade motorola/i })).toBeInTheDocument();
  });
});
