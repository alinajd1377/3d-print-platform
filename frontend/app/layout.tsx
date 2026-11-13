import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "3D Print | سفارش آنلاین پرینت سه‌بعدی",
  description: "ثبت سفارش آنلاین خدمات چاپ سه‌بعدی فیلامنتی و رزینی",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="fa" dir="rtl"><body>{children}</body></html>;
}
