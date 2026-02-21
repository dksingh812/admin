'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '@/i18n/routing';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLocaleChange = (newLocale: string) => {
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <div className="flex items-center gap-2 text-sm font-medium border-l pl-4 ml-4 h-6 border-border/40">
      <button
        onClick={() => handleLocaleChange('en')}
        className={`hover:text-brand-saffron transition-colors ${locale === 'en' ? 'text-brand-saffron font-bold' : 'text-foreground/70'}`}
        aria-label="Switch to English"
      >
        EN
      </button>
      <span className="text-foreground/30">/</span>
      <button
        onClick={() => handleLocaleChange('hi')}
        className={`hover:text-brand-saffron transition-colors ${locale === 'hi' ? 'text-brand-saffron font-bold' : 'text-foreground/70'}`}
        aria-label="हिंदी में बदलें"
      >
        HI
      </button>
    </div>
  );
}
