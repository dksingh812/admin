'use server';

import { db } from './db';

export async function getProducts(category?: string) {
  try {
    const where = category && category !== 'All' ? { category } : {};
    return await db.product.findMany({ where });
  } catch (error) {
    console.error('Error fetching products:', error);
    return [];
  }
}

export async function getOrder(id: string) {
  try {
    return await db.order.findUnique({
      where: { id },
      include: {
        user: true,
        items: {
          include: {
            product: true,
          },
        },
      },
    });
  } catch (error) {
    console.error(`Error fetching order ${id}:`, error);
    return null;
  }
}

export async function getProduct(id: string) {
  try {
    return await db.product.findUnique({
      where: { id },
    });
  } catch (error) {
    console.error(`Error fetching product ${id}:`, error);
    return null;
  }
}

export async function getFeaturedProducts() {
  try {
    return await db.product.findMany({
      take: 4,
      orderBy: { createdAt: 'desc' }, // Latest products
    });
  } catch (error) {
    console.error('Error fetching featured products:', error);
    return [];
  }
}

export async function getOrders() {
  try {
    return await db.order.findMany({
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
  } catch (error) {
    console.error('Error fetching orders:', error);
    return [];
  }
}

export async function createProduct(data: any) {
  try {
    await db.product.create({
      data: {
        name: data.name,
        description: data.description,
        ingredients: data.ingredients,
        benefits: data.benefits,
        price: parseFloat(data.price),
        category: data.category,
        stock: parseInt(data.stock),
        imageUrl: data.imageUrl,
      },
    });
    revalidatePath('/admin');
    revalidatePath('/shop');
    return { success: true };
  } catch (error) {
    console.error('Error creating product:', error);
    return { success: false, error: 'Failed to create product' };
  }
}

export async function createOrder(data: { items: any[], total: number, userId?: string, userEmail?: string }) {
  try {
    let userId = data.userId;

    // If no userId, try to find user by email or create a guest user
    if (!userId && data.userEmail) {
      const user = await db.user.findUnique({ where: { email: data.userEmail } });
      if (user) {
        userId = user.id;
      } else {
        const newUser = await db.user.create({
          data: {
            email: data.userEmail,
            name: 'Guest User',
            password: 'guest_password_placeholder', // Should act as guest
            role: 'USER',
          },
        });
        userId = newUser.id;
      }
    }

    if (!userId) {
      throw new Error('User identification failed');
    }

    const order = await db.order.create({
      data: {
        userId,
        total: data.total,
        status: 'PAID', // Simulating successful payment
        items: {
          create: data.items.map((item: any) => ({
            productId: item.id,
            quantity: item.quantity,
            price: item.price,
          })),
        },
      },
    });

    return { success: true, orderId: order.id };
  } catch (error) {
    console.error('Error creating order:', error);
    return { success: false, error: 'Failed to create order' };
  }
}
