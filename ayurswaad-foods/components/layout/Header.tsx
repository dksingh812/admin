'use client';

import { Link } from '@/i18n/routing';
import { ShoppingBag, Search, User, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';
import { useEffect, useState } from 'react';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

export function Header() {
  const { items } = useCart();
  const { user, logout } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center space-x-2">
            <span className="hidden font-bold sm:inline-block text-xl text-brand-saffron">
              Ayurswaad Foods
            </span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            <Link href="/shop" className="transition-colors hover:text-foreground/80 text-foreground/60">
              Shop
            </Link>
            <Link href="/about" className="transition-colors hover:text-foreground/80 text-foreground/60">
              About Us
            </Link>
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          <nav className="flex items-center space-x-2">
            <Link href="/cart">
              <Button variant="ghost" size="sm" className="w-9 px-0 relative">
                <ShoppingBag className="h-5 w-5" />
                <span className="sr-only">Cart</span>
                {mounted && itemCount > 0 && (
                  <span className="absolute top-0 right-0 h-4 w-4 rounded-full bg-brand-saffron text-[10px] font-bold text-white flex items-center justify-center">
                    {itemCount}
                  </span>
                )}
              </Button>
            </Link>

            {mounted && user ? (
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium hidden sm:inline-block">
                  {user.name?.split(' ')[0]}
                </span>
                {user.role === 'ADMIN' && (
                  <Link href="/admin">
                    <Button variant="ghost" size="sm">Admin</Button>
                  </Link>
                )}
                <Button variant="ghost" size="sm" onClick={() => logout()} title="Logout">
                  <LogOut className="h-5 w-5" />
                </Button>
              </div>
            ) : (
              <Link href="/login">
                <Button variant="ghost" size="sm" className="w-9 px-0">
                  <User className="h-5 w-5" />
                  <span className="sr-only">Login</span>
                </Button>
              </Link>
            )}

            <LanguageSwitcher />
          </nav>
        </div>
      </div>
    </header>
  );
}
