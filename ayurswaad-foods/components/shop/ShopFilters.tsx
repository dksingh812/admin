'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/Button';

export function ShopFilters({ activeCategory }: { activeCategory: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleCategoryChange = (category: string) => {
    // Navigate with replace to avoid adding to history stack
    const newParams = new URLSearchParams(searchParams.toString());
    if (category === 'All') {
      newParams.delete('category');
    } else {
      newParams.set('category', category);
    }
    router.replace(`?${newParams.toString()}`);
  };

  const categories = ['All', 'Laddus', 'Sethura', 'Festival Specials'];

  return (
    <div className="flex gap-2 mb-8 overflow-x-auto pb-4 no-scrollbar">
      {categories.map((cat) => (
        <Button
          key={cat}
          variant={
            (cat === 'All' && !activeCategory) || activeCategory === cat
              ? 'default'
              : 'outline'
          }
          onClick={() => handleCategoryChange(cat)}
          className={`rounded-full whitespace-nowrap px-6 ${
            (cat === 'All' && !activeCategory) || activeCategory === cat
              ? 'bg-brand-saffron text-white hover:bg-brand-saffron/90'
              : 'border-brand-saffron text-brand-saffron hover:bg-brand-saffron/10'
          }`}
        >
          {cat}
        </Button>
      ))}
    </div>
  );
}
