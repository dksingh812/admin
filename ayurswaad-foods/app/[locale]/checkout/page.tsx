'use client';

import { useState, useEffect } from 'react';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from '@/i18n/routing';
import { createOrder } from '@/lib/actions';
import { Button } from '@/components/ui/Button';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function CheckoutPage() {
  const { items, total, clearCart } = useCart();
  const { user } = useAuth();
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState<'address' | 'payment'>('address');
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    city: '',
    zip: '',
    phone: '',
  });

  useEffect(() => {
    setMounted(true);
    if (user) {
      setFormData(prev => ({ ...prev, name: user.name || '' }));
    }
  }, [user]);

  if (!mounted) return null;

  if (items.length === 0) {
    return (
      <div className="container py-12 text-center">
        <h1 className="text-2xl font-bold mb-4">Your cart is empty</h1>
        <Link href="/shop"><Button>Continue Shopping</Button></Link>
      </div>
    );
  }

  const handleAddressSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStep('payment');
  };

  const handlePayment = async () => {
    setIsProcessing(true);

    // Simulate payment delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    try {
      const result = await createOrder({
        items: items.map(item => ({
          id: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        total,
        userId: user?.id,
        userEmail: user?.email || `${formData.phone}@guest.com` // Fallback for guest
      });

      if (result.success) {
        clearCart();
        router.push(`/order-confirmation/${result.orderId}`);
      } else {
        alert('Payment failed: ' + result.error);
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('An error occurred. Please try again.');
      setIsProcessing(false);
    }
  };

  return (
    <div className="container py-12 px-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8 text-brand-brown">Checkout</h1>

      <div className="grid md:grid-cols-2 gap-12">
        {/* Left Column: Forms */}
        <div>
          {step === 'address' ? (
            <form onSubmit={handleAddressSubmit} className="space-y-4 animate-in fade-in slide-in-from-left-4 duration-500">
              <h2 className="text-xl font-semibold mb-4">Shipping Address</h2>
              <div className="space-y-2">
                <label htmlFor="fullName" className="text-sm font-medium">Full Name</label>
                <input id="fullName" required className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
                  value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div className="space-y-2">
                <label htmlFor="address" className="text-sm font-medium">Address</label>
                <textarea id="address" required className="flex w-full rounded-md border border-input px-3 py-2 text-sm min-h-[80px]"
                  value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="city" className="text-sm font-medium">City</label>
                  <input id="city" required className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
                    value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <label htmlFor="zip" className="text-sm font-medium">ZIP Code</label>
                  <input id="zip" required className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
                    value={formData.zip} onChange={e => setFormData({...formData, zip: e.target.value})} />
                </div>
              </div>
              <div className="space-y-2">
                <label htmlFor="phone" className="text-sm font-medium">Phone Number</label>
                <input id="phone" required type="tel" className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
                  value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
              </div>
              <Button type="submit" className="w-full mt-4 bg-brand-saffron hover:bg-brand-saffron/90 text-white">
                Continue to Payment
              </Button>
            </form>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Payment Method</h2>
                <Button variant="ghost" size="sm" onClick={() => setStep('address')}>Edit Address</Button>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-3 border p-4 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                  <input type="radio" name="payment" id="upi" defaultChecked className="h-4 w-4 text-brand-saffron focus:ring-brand-saffron" />
                  <label htmlFor="upi" className="flex-1 font-medium cursor-pointer">UPI (Google Pay / PhonePe)</label>
                </div>
                <div className="flex items-center space-x-3 border p-4 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                  <input type="radio" name="payment" id="card" className="h-4 w-4 text-brand-saffron focus:ring-brand-saffron" />
                  <label htmlFor="card" className="flex-1 font-medium cursor-pointer">Credit / Debit Card</label>
                </div>
                <div className="flex items-center space-x-3 border p-4 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                  <input type="radio" name="payment" id="cod" className="h-4 w-4 text-brand-saffron focus:ring-brand-saffron" />
                  <label htmlFor="cod" className="flex-1 font-medium cursor-pointer">Cash on Delivery</label>
                </div>
              </div>

              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 text-sm text-yellow-800">
                <p><strong>Note:</strong> This is a mock payment gateway. No real money will be deducted.</p>
              </div>

              <Button
                onClick={handlePayment}
                disabled={isProcessing}
                className="w-full py-6 text-lg bg-green-600 hover:bg-green-700 text-white shadow-lg"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Processing Payment...
                  </>
                ) : (
                  <>
                    Pay ₹{total.toFixed(2)}
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Right Column: Order Summary */}
        <div className="bg-muted/30 p-6 rounded-lg h-fit border">
          <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
          <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            {items.map((item) => (
              <div key={item.id} className="flex justify-between text-sm">
                <span>{item.quantity} x {item.name}</span>
                <span className="font-medium">₹{(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="border-t mt-4 pt-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Subtotal</span>
              <span>₹{total.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Shipping</span>
              <span className="text-green-600">Free</span>
            </div>
            <div className="flex justify-between font-bold text-lg pt-2 border-t mt-2">
              <span>Total</span>
              <span className="text-brand-brown">₹{total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
