import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { ModeSwitch } from "../components/chat/ModeSwitch";

test("switches from study mode to exam mode", async () => {
  const user = userEvent.setup();
  const onChange = vi.fn();
  render(<ModeSwitch value="study" onChange={onChange} />);
  await user.click(screen.getByRole("button", { name: "Ôn thi" }));
  expect(onChange).toHaveBeenCalledWith("exam");
});

