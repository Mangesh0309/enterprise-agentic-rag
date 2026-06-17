import type { ButtonHTMLAttributes, ReactNode } from "react";
import { clsx } from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: ReactNode;
  variant?: "primary" | "secondary" | "ghost";
}

export function Button({ children, icon, variant = "primary", className, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md px-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "bg-brand text-white hover:bg-[#19665B]",
        variant === "secondary" && "border border-line bg-white text-ink hover:bg-panel",
        variant === "ghost" && "text-muted hover:bg-panel hover:text-ink",
        className,
      )}
      {...props}
    >
      {icon}
      {children}
    </button>
  );
}
