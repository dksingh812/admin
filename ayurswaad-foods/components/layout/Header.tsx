'use client';

import Link from 'next/link';
import { ShoppingBag, Search, User } from 'lucide-react';
import { Button } from '../ui/Button';
import { useCart } from '@/context/CartContext';
import { useEffect, useState } from 'react';

export function Header() {
  const { items } = useCart();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <span className="hidden font-bold sm:inline-block text-xl text-brand-saffron">
            Ayurswaad Foods
          </span>
        </Link>
        <nav className="flex items-center space-x-6 text-sm font-medium">
          <Link href="/shop" className="transition-colors hover:text-foreground/80 text-foreground/60">
            Shop
          </Link>
          <Link href="/about" className="transition-colors hover:text-foreground/80 text-foreground/60">
            About Us
          </Link>
          <Link href="/blog" className="transition-colors hover:text-foreground/80 text-foreground/60">
            Ayurveda Blog
          </Link>
        </nav>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            {/* Search placeholder */}
            <Button variant="ghost" size="sm" className="w-9 px-0">
              <Search className="h-5 w-5" />
              <span className="sr-only">Search</span>
            </Button>
          </div>
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
            <Link href="/login">
              <Button variant="ghost" size="sm" className="w-9 px-0">
                <User className="h-5 w-5" />
                <span className="sr-only">Account</span>
              </Button>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
