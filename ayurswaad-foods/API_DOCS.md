# API Documentation for Ayurswaad Foods

This application uses **Next.js Server Actions** for data fetching and mutations, which is the recommended pattern for Next.js App Router. It does not expose public REST endpoints by default, but internal functions are used.

## 1. Server Actions (`lib/actions.ts`)

These functions are executed on the server and called directly from Client Components.

### Products

#### `getProducts()`
- **Description**: Fetches all products from the database.
- **Returns**: `Promise<Product[]>`
- **Example Usage**: Used in `/shop` page.

#### `getProduct(id: string)`
- **Description**: Fetches a single product by ID.
- **Parameters**: `id` (string) - The product ID.
- **Returns**: `Promise<Product | null>`
- **Example Usage**: Used in `/product/[id]` page.

#### `getFeaturedProducts()`
- **Description**: Fetches the top 3 featured products.
- **Returns**: `Promise<Product[]>`
- **Example Usage**: Used in `/` (Home) page.

### Orders

#### `createOrder(cartItems: any[], total: number, userEmail?: string)`
- **Description**: Creates a new order and associated order items.
- **Parameters**:
  - `cartItems`: Array of objects `{ id, quantity, price }`.
  - `total`: Total order amount.
  - `userEmail`: Email of the user (defaults to guest).
- **Returns**: `Promise<{ success: boolean, orderId?: string, error?: string }>`
- **Behavior**:
  - Creates a guest user if email doesn't exist.
  - Creates an Order record.
  - Creates OrderItem records for each cart item.
  - Simulates payment success (Status: PAID).

#### `getOrders()`
- **Description**: Fetches all orders (admin only).
- **Returns**: `Promise<Order[]>`
- **Example Usage**: Used in `/admin` dashboard.

## 2. Database Schema

See `SCHEMA.sql` for the full database structure.

### Models
- **User**: Represents a customer or admin.
- **Product**: Represents a sweet item.
- **Order**: Represents a purchase transaction.
- **OrderItem**: Link between Order and Product with quantity/price snapshot.

## 3. Future API Expansion

To add a public REST API (e.g., for a mobile app), create a file at `app/api/products/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
  const products = await db.product.findMany();
  return NextResponse.json(products);
}
```
Then access it via `GET /api/products`.
