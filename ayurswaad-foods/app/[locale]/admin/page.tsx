import { getOrders, getProducts } from '@/lib/actions';
import { Button } from '@/components/ui/Button';
import { Link } from '@/i18n/routing';
import { Plus, Settings, Package, ShoppingCart } from 'lucide-react';

export default async function AdminDashboard() {
  const orders = await getOrders();
  const products = await getProducts();

  return (
    <div className="container py-12 px-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-brand-brown">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">Manage your store, orders, and inventory.</p>
        </div>
        <div className="flex gap-4">
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Link href="/admin/products/new">
            <Button className="bg-brand-saffron hover:bg-brand-saffron/90 text-white">
              <Plus className="h-4 w-4 mr-2" />
              Add Product
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-12">
        {/* Orders Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <ShoppingCart className="h-6 w-6 text-brand-brown" />
              Recent Orders
            </h2>
            <span className="text-sm text-muted-foreground">{orders.length} Total</span>
          </div>
          <div className="border rounded-lg overflow-hidden bg-background shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-muted text-left">
                <tr>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider">Order ID</th>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider">Customer</th>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider">Status</th>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {orders.length > 0 ? (
                  orders.map((order) => (
                    <tr key={order.id} className="hover:bg-muted/50 transition-colors">
                      <td className="p-4 font-mono text-xs font-medium">{order.id.slice(-6).toUpperCase()}</td>
                      <td className="p-4 font-medium">{order.user?.name || order.user?.email || 'Guest'}</td>
                      <td className="p-4">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
                          order.status === 'PAID' ? 'bg-green-50 text-green-700 ring-green-600/20' :
                          order.status === 'PENDING' ? 'bg-yellow-50 text-yellow-700 ring-yellow-600/20' :
                          'bg-gray-50 text-gray-600 ring-gray-500/10'
                        }`}>
                          {order.status}
                        </span>
                      </td>
                      <td className="p-4 text-right font-medium">₹{order.total.toFixed(2)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-muted-foreground">No orders found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Products Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Package className="h-6 w-6 text-brand-brown" />
              Products Inventory
            </h2>
            <span className="text-sm text-muted-foreground">{products.length} Total</span>
          </div>
          <div className="border rounded-lg overflow-hidden bg-background shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-muted text-left">
                <tr>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider">Name</th>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider">Category</th>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider text-right">Stock</th>
                  <th className="p-4 font-medium text-muted-foreground uppercase text-xs tracking-wider text-right">Price</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {products.length > 0 ? (
                  products.map((product) => (
                    <tr key={product.id} className="hover:bg-muted/50 transition-colors">
                      <td className="p-4 font-medium">{product.name}</td>
                      <td className="p-4 text-muted-foreground">{product.category}</td>
                      <td className={`p-4 text-right font-medium ${product.stock < 10 ? 'text-red-600' : 'text-green-600'}`}>
                        {product.stock}
                      </td>
                      <td className="p-4 text-right font-medium">₹{product.price.toFixed(2)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-muted-foreground">No products found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
