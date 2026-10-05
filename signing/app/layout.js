import "./globals.css";

export const metadata = { title: "HD Sign", robots: { index: false, follow: false } };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500&family=Dancing+Script:wght@500&family=Great+Vibes&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
