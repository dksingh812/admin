import { Button } from '@/components/ui/Button';
import { ProductCard } from '@/components/product/ProductCard';
import { getFeaturedProducts } from '@/lib/actions';
import Link from 'next/link';
import Image from 'next/image';

export default async function Home() {
  const featuredProducts = await getFeaturedProducts();

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[600px] flex items-center justify-center bg-brand-saffron/10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-background/80 to-transparent z-10" />
        {/* Placeholder for hero image */}
        <div className="absolute inset-0 bg-[url('/placeholder-hero.jpg')] bg-cover bg-center opacity-50" />

        <div className="container relative z-20 text-center px-4">
          <h1 className="text-5xl md:text-7xl font-bold text-brand-brown mb-6 tracking-tight">
            The Taste of Life
          </h1>
          <p className="text-xl md:text-2xl text-foreground/80 mb-8 max-w-2xl mx-auto">
            Traditional Ayurvedic sweets made with purity, love, and legacy recipes.
            100% Homemade. No Preservatives.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/shop">
              <Button size="lg" className="bg-brand-saffron hover:bg-brand-saffron/90 text-white font-semibold px-8">
                Shop Sweets
              </Button>
            </Link>
            <Link href="/about">
              <Button size="lg" variant="outline" className="border-brand-brown text-brand-brown hover:bg-brand-brown hover:text-white">
                Our Story
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Legacy Story Section */}
      <section className="py-20 bg-brand-cream/30">
        <div className="container px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="relative aspect-video rounded-xl overflow-hidden shadow-xl">
              <div className="absolute inset-0 bg-muted flex items-center justify-center">
                <span className="text-muted-foreground">Family Tradition Image</span>
              </div>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-brand-brown mb-6">A Legacy of Purity</h2>
              <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
                Ayurswaad Foods is not just a sweet shop; it's a revival of grandmother's kitchen.
                Founded on Deepawali 2025, we bring you the authentic taste of India, prepared by women
                who understand the science of Ayurveda and the art of taste.
              </p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-brand-saffron" />
                  <span>Prepared by women with traditional recipes</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-brand-saffron" />
                  <span>Ayurvedic ingredients for health & immunity</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-brand-saffron" />
                  <span>Zero preservatives, 100% natural taste</span>
                </li>
              </ul>
              <Link href="/about">
                <Button variant="outline">Learn More About Us</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-20 container px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-brand-brown mb-4">Our Bestsellers</h2>
          <p className="text-muted-foreground">Handpicked favorites loved by families across India</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {featuredProducts.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>

        <div className="text-center mt-12">
          <Link href="/shop">
            <Button size="lg" variant="secondary">View All Products</Button>
          </Link>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-brand-brown text-brand-cream">
        <div className="container px-4 text-center">
          <h2 className="text-3xl font-bold mb-12 text-white">Why Choose Ayurswaad?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-lg bg-white/5 backdrop-blur">
              <h3 className="text-xl font-semibold mb-4 text-brand-saffron">Ayurvedic Wisdom</h3>
              <p className="text-white/80">Recipes designed to balance health and taste, using ingredients that nourish the body.</p>
            </div>
            <div className="p-6 rounded-lg bg-white/5 backdrop-blur">
              <h3 className="text-xl font-semibold mb-4 text-brand-saffron">Women-Led</h3>
              <p className="text-white/80">Empowering women artisans who put their heart and soul into every laddu they roll.</p>
            </div>
            <div className="p-6 rounded-lg bg-white/5 backdrop-blur">
              <h3 className="text-xl font-semibold mb-4 text-brand-saffron">Pure Ingredients</h3>
              <p className="text-white/80">Only the finest Ghee, Jaggery, and Nuts. Absolutely no artificial colors or chemicals.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
