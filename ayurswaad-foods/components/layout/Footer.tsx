import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t bg-muted">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="mb-4 flex items-center space-x-2">
              <span className="text-xl font-bold text-primary">Ayurswaad Foods</span>
            </Link>
            <p className="text-sm text-muted-foreground">
              Traditional Ayurvedic-inspired sweet brand focused on purity, legacy taste, and family values.
            </p>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold text-foreground">Shop</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link href="/shop" className="hover:text-primary">All Products</Link></li>
              <li><Link href="/shop/laddus" className="hover:text-primary">Laddus</Link></li>
              <li><Link href="/shop/sethura" className="hover:text-primary">Sethura</Link></li>
              <li><Link href="/shop/festival" className="hover:text-primary">Festival Specials</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold text-foreground">Company</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link href="/about" className="hover:text-primary">About Us</Link></li>
              <li><Link href="/process" className="hover:text-primary">Our Process</Link></li>
              <li><Link href="/blog" className="hover:text-primary">Ayurveda Blog</Link></li>
              <li><Link href="/contact" className="hover:text-primary">Contact Us</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold text-foreground">Policies</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link href="/privacy" className="hover:text-primary">Privacy Policy</Link></li>
              <li><Link href="/refund" className="hover:text-primary">Refund Policy</Link></li>
              <li><Link href="/shipping" className="hover:text-primary">Shipping Policy</Link></li>
              <li><Link href="/faq" className="hover:text-primary">FAQ</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Ayurswaad Foods. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
