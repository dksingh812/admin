import { getOrders, getProducts } from '@/lib/actions';
import { Button } from '@/components/ui/Button';

export default async function AdminDashboard() {
  const orders = await getOrders();
  const products = await getProducts();

  return (
    <div className="container py-12 px-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-brand-brown">Admin Dashboard</h1>
        <div className="space-x-4">
          <Button variant="outline">Settings</Button>
          <Button>Add Product</Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-12">
        {/* Orders Section */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Recent Orders</h2>
          <div className="border rounded-lg overflow-hidden bg-background shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-muted text-left">
                <tr>
                  <th className="p-4 font-medium">Order ID</th>
                  <th className="p-4 font-medium">Customer</th>
                  <th className="p-4 font-medium">Status</th>
                  <th className="p-4 font-medium text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {orders.length > 0 ? (
                  orders.map((order) => (
                    <tr key={order.id}>
                      <td className="p-4 font-mono text-xs">{order.id.slice(-6)}</td>
                      <td className="p-4">{order.user?.name || order.user?.email || 'Guest'}</td>
                      <td className="p-4">
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${
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
                    <td colSpan={4} className="p-4 text-center text-muted-foreground">No orders found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Products Section */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Products Inventory</h2>
          <div className="border rounded-lg overflow-hidden bg-background shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-muted text-left">
                <tr>
                  <th className="p-4 font-medium">Name</th>
                  <th className="p-4 font-medium">Category</th>
                  <th className="p-4 font-medium text-right">Stock</th>
                  <th className="p-4 font-medium text-right">Price</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {products.length > 0 ? (
                  products.map((product) => (
                    <tr key={product.id}>
                      <td className="p-4 font-medium">{product.name}</td>
                      <td className="p-4 text-muted-foreground">{product.category}</td>
                      <td className="p-4 text-right">{product.stock}</td>
                      <td className="p-4 text-right">₹{product.price.toFixed(2)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="p-4 text-center text-muted-foreground">No products found.</td>
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
