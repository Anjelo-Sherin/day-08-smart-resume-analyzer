import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RoleFit AI — Smart Resume Analyzer & Job Matcher (Day 08)",
  description:
    "Day 08 of 30 Projects in 30 Days: Upload a resume PDF/DOCX, compute an explainable Hybrid ATS Score, identify skill gaps with a curated learning path, rank best-fit job roles via vector search, and rewrite weak bullets with Gemini 3.8 Flash.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-primary selection:text-white">
        {children}
      </body>
    </html>
  );
}
