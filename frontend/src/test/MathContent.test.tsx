import { render } from "@testing-library/react";
import { MathContent } from "../components/math/MathContent";

test("renders inline LaTeX with KaTeX", () => {
  const { container } = render(<MathContent>{"Công thức $x^2 + 1$."}</MathContent>);
  expect(container.querySelector(".katex")).toBeInTheDocument();
});

