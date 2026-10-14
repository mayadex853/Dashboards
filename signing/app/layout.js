import "./globals.css";
import Toaster from "@/components/Toast";

export const metadata = { title: "TakaSign", robots: { index: false, follow: false } };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Caveat:wght@500&family=Dancing+Script:wght@500&family=Great+Vibes&family=Homemade+Apple&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
