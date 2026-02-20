'use server';

import { db } from './db';
import { revalidatePath } from 'next/cache';

export async function getProducts() {
  try {
    const products = await db.product.findMany();
    return products;
  } catch (error) {
    console.error('Error fetching products:', error);
    return [];
  }
}

export async function getProduct(id: string) {
  try {
    const product = await db.product.findUnique({
      where: { id },
    });
    return product;
  } catch (error) {
    console.error(`Error fetching product ${id}:`, error);
    return null;
  }
}

export async function getFeaturedProducts() {
  try {
    // For now, just return first 3 products as featured
    const products = await db.product.findMany({
      take: 3,
    });
    return products;
  } catch (error) {
    console.error('Error fetching featured products:', error);
    return [];
  }
}

// Mock checkout action
export async function getOrders() {
  try {
    const orders = await db.order.findMany({
      include: {
        user: true,
        items: {
          include: {
            product: true,
          },
        },
      },
      orderBy: {
        createdAt: 'desc',
      },
    });
    return orders;
  } catch (error) {
    console.error('Error fetching orders:', error);
    return [];
  }
}

export async function createOrder(cartItems: any[], total: number, userEmail: string = 'guest@example.com') {
  try {
    // In a real app, we would get the user from the session
    // For this demo, we'll create a guest user if not exists or use a default one
    let user = await db.user.findUnique({ where: { email: userEmail } });

    if (!user) {
      user = await db.user.create({
        data: {
          email: userEmail,
          name: 'Guest User',
          password: 'hashed_password_placeholder', // Should be hashed
        },
      });
    }

    const order = await db.order.create({
      data: {
        userId: user.id,
        total,
        status: 'PAID', // Simulating successful payment
        items: {
          create: cartItems.map((item: any) => ({
            productId: item.id,
            quantity: item.quantity,
            price: item.price,
          })),
        },
      },
    });

    revalidatePath('/admin');
    return { success: true, orderId: order.id };
  } catch (error) {
    console.error('Error creating order:', error);
    return { success: false, error: 'Failed to create order' };
  }
}
