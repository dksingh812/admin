import { getProducts } from '@/lib/actions';
import { ProductCard } from '@/components/product/ProductCard';

export default async function ShopPage() {
  const products = await getProducts();

  return (
    <div className="container py-12 px-4">
      <h1 className="text-3xl font-bold mb-8 text-brand-brown">Shop All Sweets</h1>

      {/* Categories / Filter Placeholder */}
      <div className="flex gap-4 mb-8 overflow-x-auto pb-4">
        <button className="px-4 py-2 rounded-full bg-brand-saffron text-white font-medium">All</button>
        <button className="px-4 py-2 rounded-full bg-muted hover:bg-muted/80 text-foreground font-medium">Laddus</button>
        <button className="px-4 py-2 rounded-full bg-muted hover:bg-muted/80 text-foreground font-medium">Sethura</button>
        <button className="px-4 py-2 rounded-full bg-muted hover:bg-muted/80 text-foreground font-medium">Festival Specials</button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.length > 0 ? (
          products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))
        ) : (
          <p className="col-span-full text-center text-muted-foreground">No products found.</p>
        )}
      </div>
    </div>
  );
}
