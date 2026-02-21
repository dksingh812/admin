import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  // Create Admin User
  const adminEmail = 'admin@ayurswaad.com';
  const existingAdmin = await prisma.user.findUnique({
    where: { email: adminEmail },
  });

  if (!existingAdmin) {
    const hashedPassword = await bcrypt.hash('admin123', 10);
    await prisma.user.create({
      data: {
        email: adminEmail,
        password: hashedPassword,
        name: 'Admin',
        role: 'ADMIN',
      },
    });
    console.log('Admin user created');
  } else {
    console.log('Admin user already exists');
  }

  // Create Products
  const products = [
    {
      name: 'Besan Ladoo (Special)',
      description: 'Rich with pure Ghee and premium nuts, perfect for celebrations.',
      ingredients: 'Gram flour, Pure Desi Ghee, Sugar, Cardamom, Cashews, Raisins',
      benefits: 'High protein, good source of healthy fats, boosts immunity.',
      price: 450,
      category: 'Laddus',
      stock: 50,
      imageUrl: '/images/products/besan-ladoo.jpg', // Placeholder
    },
    {
      name: 'Kaju Katli Box',
      description: 'Authentic, pure cashew delight. A must-have for every festival.',
      ingredients: 'Cashew nuts, Sugar, Silver Vark',
      benefits: 'Rich in antioxidants, good for heart health in moderation.',
      price: 850,
      category: 'Festival Specials',
      stock: 30,
      imageUrl: '/images/products/kaju-katli.jpg', // Placeholder
    },
    {
      name: 'Mysore Pak',
      description: 'Melt-in-your-mouth texture with the perfect sweetness.',
      ingredients: 'Chickpea flour, Ghee, Sugar',
      benefits: 'Provides instant energy, traditional taste.',
      price: 550,
      category: 'Festival Specials',
      stock: 40,
      imageUrl: '/images/products/mysore-pak.jpg', // Placeholder
    },
    {
      name: 'Sethura (Traditional)',
      description: 'A traditional sweet/snack often made during festivals.',
      ingredients: 'Whole wheat flour, Jaggery, Ghee',
      benefits: 'Iron-rich due to jaggery, wholesome energy.',
      price: 300,
      category: 'Sethura',
      stock: 60,
      imageUrl: '/images/products/sethura.jpg', // Placeholder
    },
    {
      name: 'Gond Ladoo',
      description: 'Perfect winter sweet for joint health and immunity.',
      ingredients: 'Edible gum (Gond), Wheat flour, Ghee, Dry fruits',
      benefits: 'Strengthens bones, boosts immunity, good for post-pregnancy.',
      price: 600,
      category: 'Laddus',
      stock: 25,
      imageUrl: '/images/products/gond-ladoo.jpg', // Placeholder
    },
  ];

  for (const product of products) {
    const existingProduct = await prisma.product.findFirst({
      where: { name: product.name },
    });

    if (!existingProduct) {
      await prisma.product.create({
        data: product,
      });
      console.log(`Product created: ${product.name}`);
    } else {
      console.log(`Product already exists: ${product.name}`);
    }
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
