'use client';

import { useState } from 'react';
import { createProduct } from '@/lib/actions';
import { Button } from '@/components/ui/Button';
import { useRouter } from '@/i18n/routing';
import { ArrowLeft, Loader2, Save } from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function AddProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: 'Laddus',
    stock: '10',
    ingredients: '',
    benefits: '',
    imageUrl: '/images/products/placeholder.jpg',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await createProduct({
        ...formData,
        price: parseFloat(formData.price),
        stock: parseInt(formData.stock),
      });

      if (result.success) {
        router.push('/admin');
        router.refresh();
      } else {
        alert('Failed to create product: ' + result.error);
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-12 px-4 max-w-2xl">
      <div className="flex items-center gap-4 mb-8">
        <Link href="/admin">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" /> Back
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-brand-brown">Add New Product</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-card p-6 rounded-lg border shadow-sm">
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Product Name</label>
            <input required name="name" className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
              value={formData.name} onChange={handleChange} placeholder="e.g. Besan Ladoo" />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Category</label>
            <select name="category" className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm bg-background"
              value={formData.category} onChange={handleChange}>
              <option value="Laddus">Laddus</option>
              <option value="Sethura">Sethura</option>
              <option value="Festival Specials">Festival Specials</option>
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Description</label>
          <textarea required name="description" className="flex w-full rounded-md border border-input px-3 py-2 text-sm min-h-[80px]"
            value={formData.description} onChange={handleChange} placeholder="Short description..." />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Price (₹)</label>
            <input required type="number" name="price" min="0" step="0.01" className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
              value={formData.price} onChange={handleChange} placeholder="0.00" />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Initial Stock</label>
            <input required type="number" name="stock" min="0" className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
              value={formData.stock} onChange={handleChange} />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Ingredients</label>
          <textarea name="ingredients" className="flex w-full rounded-md border border-input px-3 py-2 text-sm min-h-[60px]"
            value={formData.ingredients} onChange={handleChange} placeholder="List ingredients separated by commas..." />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Ayurvedic Benefits</label>
          <textarea name="benefits" className="flex w-full rounded-md border border-input px-3 py-2 text-sm min-h-[60px]"
            value={formData.benefits} onChange={handleChange} placeholder="Describe health benefits..." />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Image URL</label>
          <input name="imageUrl" className="flex h-10 w-full rounded-md border border-input px-3 py-2 text-sm"
            value={formData.imageUrl} onChange={handleChange} placeholder="https://example.com/image.jpg" />
          <p className="text-xs text-muted-foreground">Enter a public image URL or keep default placeholder.</p>
        </div>

        <div className="pt-4 flex justify-end gap-4">
          <Link href="/admin">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
          <Button type="submit" disabled={loading} className="bg-brand-saffron hover:bg-brand-saffron/90 text-white min-w-[150px]">
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            {loading ? 'Creating...' : 'Create Product'}
          </Button>
        </div>
      </form>
    </div>
  );
}
