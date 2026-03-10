import { Star } from 'lucide-react';
import { useTranslations } from 'next-intl';

export function Testimonials() {
  const t = useTranslations('Home.Testimonials');

  const testimonials = [
    {
      id: 1,
      name: "Anjali Sharma",
      role: t('list.0.role'),
      content: t('list.0.content'),
      rating: 5
    },
    {
      id: 2,
      name: "Rahul Verma",
      role: t('list.1.role'),
      content: t('list.1.content'),
      rating: 5
    },
    {
      id: 3,
      name: "Sneha Patel",
      role: t('list.2.role'),
      content: t('list.2.content'),
      rating: 4
    }
  ];

  return (
    <section className="py-20 bg-brand-cream/30">
      <div className="container px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-brand-brown mb-4">{t('title')}</h2>
          <div className="h-1 w-20 bg-brand-saffron mx-auto rounded-full"></div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.id} className="bg-background p-8 rounded-xl shadow-sm border border-border/50 hover:shadow-md transition-shadow">
              <div className="flex gap-1 mb-4 text-brand-saffron">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    size={18}
                    fill={i < testimonial.rating ? "currentColor" : "none"}
                    className={i < testimonial.rating ? "text-brand-saffron" : "text-muted-foreground/30"}
                  />
                ))}
              </div>
              <p className="text-foreground/80 mb-6 italic leading-relaxed">"{testimonial.content}"</p>
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-brand-saffron/20 flex items-center justify-center text-brand-brown font-bold">
                  {testimonial.name[0]}
                </div>
                <div>
                  <h4 className="font-semibold text-brand-brown">{testimonial.name}</h4>
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">{testimonial.role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
