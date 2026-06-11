import clsx, { type ClassValue } from "clsx";

export function cn(...values: ClassValue[]): string {
  return clsx(values);
}

export const contentLabels: Record<string, string> = {
  theory: "Lý thuyết",
  formula: "Công thức",
  example: "Ví dụ",
  exam: "Đề thi",
  solution: "Lời giải",
};

