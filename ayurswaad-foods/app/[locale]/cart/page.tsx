'use client';

import { useCart } from '@/context/CartContext';
import { Button } from '@/components/ui/Button';
import { Link } from '@/i18n/routing';
import Image from 'next/image';
import { Trash2, ShoppingBag, ArrowRight } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function CartPage() {
  const { items, removeFromCart, updateQuantity, total } = useCart();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null; // Avoid hydration mismatch

  if (items.length === 0) {
    return (
      <div className="container flex flex-col items-center justify-center min-h-[60vh] py-12 px-4 text-center">
        <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-6">
          <ShoppingBag className="h-12 w-12 text-muted-foreground" />
        </div>
        <h1 className="text-3xl font-bold mb-4 text-brand-brown">Your Cart is Empty</h1>
        <p className="text-muted-foreground mb-8 max-w-md">
          Looks like you haven't added any sweets to your cart yet. Explore our collection of traditional delights.
        </p>
        <Link href="/shop">
          <Button size="lg" className="bg-brand-saffron hover:bg-brand-saffron/90 text-white px-8">
            Start Shopping
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container py-12 px-4">
      <h1 className="text-3xl font-bold mb-8 text-brand-brown">Shopping Cart ({items.length})</h1>

      <div className="grid lg:grid-cols-3 gap-12">
        <div className="lg:col-span-2 space-y-6">
          {items.map((item) => (
            <div key={item.id} className="flex gap-4 p-4 border rounded-lg bg-card shadow-sm items-center">
              <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-md border bg-muted">
                <Image
                  src={item.imageUrl || "/placeholder.jpg"}
                  alt={item.name}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="flex flex-1 flex-col justify-between space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{item.name}</h3>
                    <p className="text-sm text-muted-foreground">₹{item.price.toFixed(2)} / unit</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    onClick={() => removeFromCart(item.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                    <span className="sr-only">Remove</span>
                  </Button>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center border rounded-md">
                    <button
                      className="px-3 py-1 hover:bg-muted text-lg"
                      onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                    >-</button>
                    <span className="px-3 py-1 font-mono">{item.quantity}</span>
                    <button
                      className="px-3 py-1 hover:bg-muted text-lg"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    >+</button>
                  </div>
                  <div className="font-bold text-lg text-brand-brown">
                    ₹{(item.price * item.quantity).toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <div className="bg-card border rounded-lg p-6 shadow-sm sticky top-24">
            <h2 className="text-xl font-semibold mb-6">Order Summary</h2>
            <div className="space-y-4 mb-6">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subtotal</span>
                <span className="font-medium">₹{total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Shipping</span>
                <span className="text-green-600 font-medium">Free</span>
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Tax (GST Included)</span>
                <span>₹{(total * 0.05).toFixed(2)}</span>
              </div>
              <div className="border-t pt-4 flex justify-between items-end">
                <span className="font-bold text-lg">Total</span>
                <span className="font-bold text-2xl text-brand-brown">₹{total.toFixed(2)}</span>
              </div>
            </div>

            <Link href="/checkout" className="w-full block">
              <Button size="lg" className="w-full bg-brand-saffron hover:bg-brand-saffron/90 text-white font-semibold shadow-md hover:shadow-lg transition-all">
                Proceed to Checkout <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>

            <div className="mt-6 text-center text-xs text-muted-foreground flex flex-col gap-2">
              <p>Secure Checkout powered by MockPay</p>
              <div className="flex justify-center gap-2 opacity-50">
                {/* Icons placeholder */}
                <span>VISA</span>
                <span>Mastercard</span>
                <span>UPI</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
