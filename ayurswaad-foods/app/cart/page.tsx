'use client';

import { useCart } from '@/context/CartContext';
import { Button } from '@/components/ui/Button';
import Image from 'next/image';
import Link from 'next/link';
import { createOrder } from '@/lib/actions';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CartPage() {
  const { items, removeFromCart, clearCart, total } = useCart();
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const router = useRouter();

  const handleCheckout = async () => {
    setIsCheckingOut(true);

    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Create order on server
    const result = await createOrder(items, total);

    if (result.success) {
      clearCart();
      alert(`Order placed successfully! Order ID: ${result.orderId}`);
      router.push('/');
    } else {
      alert('Failed to place order. Please try again.');
    }

    setIsCheckingOut(false);
  };

  if (items.length === 0) {
    return (
      <div className="container py-20 text-center">
        <h1 className="text-3xl font-bold mb-6">Your Cart is Empty</h1>
        <p className="text-muted-foreground mb-8">Looks like you haven't added any sweets yet.</p>
        <Link href="/shop">
          <Button size="lg">Start Shopping</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container py-12 px-4">
      <h1 className="text-3xl font-bold mb-8 text-brand-brown">Your Shopping Cart</h1>

      <div className="grid lg:grid-cols-3 gap-12">
        <div className="lg:col-span-2 space-y-6">
          {items.map((item) => (
            <div key={item.id} className="flex gap-4 border rounded-lg p-4 bg-background shadow-sm">
              <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-md border bg-muted">
                <Image
                  src={item.imageUrl || "/placeholder.jpg"}
                  alt={item.name}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="flex flex-1 flex-col justify-between">
                <div className="grid gap-1">
                  <h3 className="font-semibold">{item.name}</h3>
                  <p className="text-sm text-muted-foreground">Price: ₹{item.price.toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground">Qty: {item.quantity}</p>
                </div>
                <div className="flex items-center justify-between">
                  <p className="font-medium">₹{(item.price * item.quantity).toFixed(2)}</p>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500 hover:text-red-600 hover:bg-red-50"
                    onClick={() => removeFromCart(item.id)}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <div className="border rounded-lg p-6 bg-muted/30 sticky top-24">
            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span>Subtotal</span>
                <span>₹{total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Shipping</span>
                <span>Free</span>
              </div>
              <div className="border-t pt-2 mt-2 flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>₹{total.toFixed(2)}</span>
              </div>
            </div>
            <Button
              className="w-full bg-brand-saffron hover:bg-brand-saffron/90 text-white"
              size="lg"
              onClick={handleCheckout}
              disabled={isCheckingOut}
            >
              {isCheckingOut ? 'Processing...' : 'Proceed to Checkout'}
            </Button>
            <p className="text-xs text-center mt-4 text-muted-foreground">
              Secure Checkout via Mock Payment Gateway
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
