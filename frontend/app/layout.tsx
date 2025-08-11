// dashboard/app/layout.tsx

import './styles/globals.css';
import ClientLayout from './components/ClientLayout';

export const metadata = {
  title: 'ZeroDev AI',
  description: 'Next-level developer automation for everyone',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
