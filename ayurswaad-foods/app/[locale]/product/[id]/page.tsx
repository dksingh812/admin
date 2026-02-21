import { getProduct } from '@/lib/actions';
import { AddToCartSection } from '@/components/product/AddToCartSection';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Image from 'next/image';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const product = await getProduct(id);
  if (!product) return { title: 'Product Not Found' };
  return {
    title: `${product.name} - Ayurswaad Foods`,
    description: product.description,
  };
}

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);

  if (!product) {
    notFound();
  }

  return (
    <div className="container py-12 px-4">
      <div className="grid md:grid-cols-2 gap-12 lg:gap-16">
        {/* Product Image */}
        <div className="relative aspect-square md:aspect-[4/3] lg:aspect-square w-full overflow-hidden rounded-xl bg-muted shadow-lg border border-border/50">
          <Image
            src={product.imageUrl || "/placeholder.jpg"}
            alt={product.name}
            fill
            className="object-cover transition-transform hover:scale-105 duration-500"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            priority
          />
        </div>

        {/* Product Details */}
        <div className="flex flex-col justify-start space-y-8">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 text-xs font-semibold tracking-wider uppercase bg-brand-saffron/10 text-brand-saffron rounded-full">
                {product.category}
              </span>
              {product.stock > 0 ? (
                <span className="text-xs text-green-600 font-medium">In Stock</span>
              ) : (
                <span className="text-xs text-red-600 font-medium">Out of Stock</span>
              )}
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-brand-brown tracking-tight mb-4">
              {product.name}
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              {product.description}
            </p>
          </div>

          <div className="flex items-baseline gap-4 border-b pb-8 border-border/50">
            <span className="text-4xl font-bold text-brand-saffron">
              ₹{product.price.toFixed(2)}
            </span>
            <span className="text-sm text-muted-foreground line-through">
              ₹{(product.price * 1.2).toFixed(2)}
            </span>
            <span className="text-sm font-medium text-green-600">
              (Save 20%)
            </span>
          </div>

          <AddToCartSection product={{
            id: product.id,
            name: product.name,
            price: product.price,
            imageUrl: product.imageUrl
          }} />

          {/* Additional Info Tabs/Sections */}
          <div className="grid gap-6 pt-6">
            <div className="bg-brand-cream/20 p-6 rounded-lg border border-brand-cream/40">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-brand-brown">
                <span className="h-2 w-2 rounded-full bg-brand-saffron" />
                Ingredients
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {product.ingredients || 'Natural ingredients used.'}
              </p>
            </div>

            <div className="bg-green-50/50 p-6 rounded-lg border border-green-100">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-brand-brown">
                <span className="h-2 w-2 rounded-full bg-green-600" />
                Ayurvedic Benefits
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {product.benefits || 'Promotes overall health and wellness.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
