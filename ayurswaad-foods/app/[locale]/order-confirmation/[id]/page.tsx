import { getOrder } from '@/lib/actions';
import { notFound } from 'next/navigation';
import { CheckCircle2, Package } from 'lucide-react';
import { Link } from '@/i18n/routing';
import { Button } from '@/components/ui/Button';

export default async function OrderConfirmationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const order = await getOrder(id);

  if (!order) notFound();

  return (
    <div className="container py-12 px-4 flex flex-col items-center max-w-2xl text-center animate-in fade-in zoom-in duration-500">
      <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
        <CheckCircle2 className="h-12 w-12 text-green-600" />
      </div>
      <h1 className="text-3xl font-bold mb-4 text-brand-brown">Order Confirmed!</h1>
      <p className="text-muted-foreground mb-8">
        Thank you for choosing Ayurswaad. We are preparing your order with love and care.
      </p>

      <div className="w-full bg-card border rounded-lg p-6 shadow-sm mb-8 text-left relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-brand-saffron" />
        <div className="flex justify-between items-center mb-4 pb-4 border-b border-dashed">
          <div>
            <span className="block text-xs text-muted-foreground uppercase tracking-wide">Order ID</span>
            <span className="font-mono font-bold text-lg text-brand-brown">#{order.id.slice(-6).toUpperCase()}</span>
          </div>
          <div className="text-right">
            <span className="block text-xs text-muted-foreground uppercase tracking-wide">Date</span>
            <span className="text-sm font-medium">{new Date(order.createdAt).toLocaleDateString()}</span>
          </div>
        </div>

        <div className="space-y-3 mb-6">
           {order.items.map((item: any) => (
             <div key={item.id} className="flex justify-between text-sm items-center">
               <div className="flex items-center gap-2">
                 <span className="w-6 h-6 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-muted-foreground">
                   {item.quantity}
                 </span>
                 <span>{item.product.name}</span>
               </div>
               <span className="font-medium text-brand-brown">₹{(item.price * item.quantity).toFixed(2)}</span>
             </div>
           ))}
        </div>

        <div className="border-t border-dashed pt-4 flex justify-between items-end">
          <span className="text-sm font-medium text-muted-foreground">Total Amount Paid</span>
          <span className="font-bold text-2xl text-brand-brown">₹{order.total.toFixed(2)}</span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
        <Link href="/shop">
          <Button variant="outline" className="w-full sm:w-auto border-brand-brown text-brand-brown hover:bg-brand-brown/10">
            Continue Shopping
          </Button>
        </Link>
        <Link href="/">
          <Button className="w-full sm:w-auto bg-brand-saffron hover:bg-brand-saffron/90 text-white">
            Return Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
