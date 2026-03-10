'use client';

import { Button } from '../ui/Button';
import { useTranslations } from 'next-intl';

export function Newsletter() {
  const t = useTranslations('Home.Newsletter');

  return (
    <section className="py-20 bg-brand-brown text-brand-cream relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
        <div className="absolute top-10 left-10 w-32 h-32 rounded-full bg-brand-saffron blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 rounded-full bg-brand-saffron blur-3xl"></div>
      </div>

      <div className="container px-4 relative z-10 text-center max-w-3xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">{t('title')}</h2>
        <p className="text-white/80 text-lg mb-10 leading-relaxed">
          {t('description')}
        </p>

        <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto" onSubmit={(e) => e.preventDefault()}>
          <input
            type="email"
            placeholder={t('placeholder')}
            className="flex-1 px-6 py-4 rounded-lg bg-white/10 border border-white/20 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-brand-saffron transition-all"
            required
          />
          <Button size="lg" className="bg-brand-saffron hover:bg-brand-saffron/90 text-white font-semibold px-8 py-4 h-auto">
            {t('button')}
          </Button>
        </form>

        <p className="mt-6 text-sm text-white/50">
          {t('privacy')}
        </p>
      </div>
    </section>
  );
}
