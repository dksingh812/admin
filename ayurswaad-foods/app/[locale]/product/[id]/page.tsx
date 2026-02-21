import { getProduct } from '@/lib/actions';
import { AddToCartButton } from '@/components/product/AddToCartButton';
import Image from 'next/image';
import { notFound } from 'next/navigation';

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);

  if (!product) {
    notFound();
  }

  return (
    <div className="container py-12 px-4">
      <div className="grid md:grid-cols-2 gap-12">
        {/* Product Image */}
        <div className="relative aspect-square bg-muted rounded-xl overflow-hidden shadow-lg">
          <Image
            src={product.imageUrl || "/placeholder.jpg"}
            alt={product.name}
            fill
            className="object-cover"
            priority
          />
        </div>

        {/* Product Details */}
        <div>
          <h1 className="text-4xl font-bold text-brand-brown mb-2">{product.name}</h1>
          <p className="text-lg text-brand-saffron font-medium mb-6">{product.category}</p>

          <div className="text-3xl font-bold text-foreground mb-8">
            ₹{product.price.toFixed(2)}
            <span className="text-sm font-normal text-muted-foreground ml-2">/ 500g</span>
          </div>

          <div className="prose prose-stone mb-8">
            <h3 className="text-xl font-semibold mb-2">Description</h3>
            <p className="text-muted-foreground mb-4">{product.description}</p>

            <h3 className="text-xl font-semibold mb-2">Ayurvedic Benefits</h3>
            <p className="text-muted-foreground mb-4">{product.benefits}</p>

            <h3 className="text-xl font-semibold mb-2">Ingredients</h3>
            <p className="text-muted-foreground mb-4">{product.ingredients}</p>
          </div>

          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">Quantity:</span>
              <select className="border rounded p-2 bg-background">
                <option value="1">1 (500g)</option>
                <option value="2">2 (1kg)</option>
                <option value="3">3 (1.5kg)</option>
              </select>
            </div>

            <AddToCartButton product={product} />
          </div>

          <div className="mt-8 border-t pt-8 text-sm text-muted-foreground">
            <p className="mb-2">✓ 100% Homemade by Women Artisans</p>
            <p className="mb-2">✓ No Preservatives or Artificial Colors</p>
            <p>✓ Secure Packaging & Fast Delivery</p>
          </div>
        </div>
      </div>
    </div>
  );
}
