import { getProducts } from '@/lib/actions';
import { ProductCard } from '@/components/product/ProductCard';
import { ShopFilters } from '@/components/shop/ShopFilters';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Shop - Ayurswaad Foods',
  description: 'Browse our collection of traditional Ayurvedic sweets.',
};

export default async function ShopPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string }>;
}) {
  const params = await searchParams;
  const category = params.category || 'All';
  const products = await getProducts(category);

  return (
    <div className="container py-12 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-brand-brown">Shop Sweets</h1>
          <p className="text-muted-foreground mt-1">Authentic taste of tradition</p>
        </div>
      </div>

      <ShopFilters activeCategory={category} />

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.length > 0 ? (
          products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))
        ) : (
          <div className="col-span-full py-12 text-center bg-muted/30 rounded-lg">
            <p className="text-lg text-muted-foreground">No products found in this category.</p>
          </div>
        )}
      </div>
    </div>
  );
}
