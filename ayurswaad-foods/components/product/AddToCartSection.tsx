'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { useCart } from '@/context/CartContext';
import { Minus, Plus, ShoppingBag } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  price: number;
  imageUrl: string | null;
}

export function AddToCartSection({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = useCart();
  const [added, setAdded] = useState(false);

  const handleAdd = () => {
    addToCart(product, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6 mt-8 p-6 bg-muted/30 rounded-lg border border-brand-saffron/20">
      <div className="flex items-center justify-between">
        <span className="text-lg font-medium text-brand-brown">Select Quantity:</span>
        <div className="flex items-center border bg-background rounded-md shadow-sm">
          <Button
            variant="ghost"
            size="sm"
            className="h-10 w-10 p-0 hover:bg-muted"
            onClick={() => setQuantity(Math.max(1, quantity - 1))}
            disabled={quantity <= 1}
          >
            <Minus className="h-4 w-4" />
          </Button>
          <span className="w-12 text-center font-mono text-lg">{quantity}</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-10 w-10 p-0 hover:bg-muted"
            onClick={() => setQuantity(quantity + 1)}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-end mb-2">
          <span className="text-sm text-muted-foreground">Total Price:</span>
          <span className="text-2xl font-bold text-brand-brown">₹{(product.price * quantity).toFixed(2)}</span>
        </div>
        <Button
          size="lg"
          className={`w-full transition-all ${
            added
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-brand-saffron hover:bg-brand-saffron/90 text-white'
          }`}
          onClick={handleAdd}
          disabled={added}
        >
          {added ? (
            <span className="flex items-center justify-center gap-2">
              Added to Cart ✓
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <ShoppingBag className="h-5 w-5" />
              Add to Cart
            </span>
          )}
        </Button>
      </div>

      <p className="text-xs text-center text-muted-foreground">
        Secure checkout • 100% Authentic • Freshly Prepared
      </p>
    </div>
  );
}
