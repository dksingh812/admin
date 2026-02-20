'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { useCart } from '@/context/CartContext';

interface AddToCartButtonProps {
  product: any;
}

export function AddToCartButton({ product }: AddToCartButtonProps) {
  const [loading, setLoading] = useState(false);
  const { addToCart } = useCart();

  const handleAddToCart = () => {
    setLoading(true);
    // Simulate slight delay for feedback
    setTimeout(() => {
      addToCart(product);
      setLoading(false);
      // Optional: Add toast notification here
      alert(`${product.name} added to cart!`);
    }, 500);
  };

  return (
    <Button
      size="lg"
      onClick={handleAddToCart}
      disabled={loading}
      className="w-full md:w-auto px-8 bg-brand-saffron hover:bg-brand-saffron/90 text-white"
    >
      {loading ? 'Adding...' : 'Add to Cart'}
    </Button>
  );
}
