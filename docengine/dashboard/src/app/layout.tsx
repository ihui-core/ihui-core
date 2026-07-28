import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ihui Core-Doc-Engine",
  description: "Observabilidad determinista de agentes y documentacion",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
