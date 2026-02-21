import Link from 'next/link';
import { Button } from '../ui/Button';
import { ProductCard } from '../product/ProductCard';
import { useTranslations } from 'next-intl';

export function FestivalSpecial() {
  const t = useTranslations('Home.Festival');

  // Mock data for Festival Specials
  const products = [
    {
      id: "f1",
      name: t('products.f1.name'),
      description: t('products.f1.description'),
      price: 450,
      imageUrl: "/placeholder.jpg"
    },
    {
      id: "f2",
      name: t('products.f2.name'),
      description: t('products.f2.description'),
      price: 850,
      imageUrl: "/placeholder.jpg"
    },
    {
      id: "f3",
      name: t('products.f3.name'),
      description: t('products.f3.description'),
      price: 520,
      imageUrl: "/placeholder.jpg"
    },
    {
      id: "f4",
      name: t('products.f4.name'),
      description: t('products.f4.description'),
      price: 1200,
      imageUrl: "/placeholder.jpg"
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-brand-saffron/10 via-background to-brand-cream/20">
      <div className="container px-4">
        <div className="text-center mb-12">
          <span className="text-brand-saffron font-medium uppercase tracking-widest text-sm mb-2 block">{t('tag')}</span>
          <h2 className="text-4xl md:text-5xl font-bold text-brand-brown mb-4 font-serif">{t('title')}</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            {t('description')}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {products.map((product) => (
            <div key={product.id} className="relative group">
              {/* Decorative Border */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-brand-saffron to-brand-brown opacity-20 group-hover:opacity-100 rounded-lg blur transition duration-500"></div>
              <div className="relative bg-background rounded-lg">
                <ProductCard product={product} />
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link href="/shop?category=festival">
            <Button size="lg" className="bg-brand-brown text-white hover:bg-brand-brown/90 px-8 py-6 text-lg">
              {t('button')}
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
