const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const products = [
    {
      name: "Besan Laddu",
      description: "Traditional homemade Besan Laddu made with pure ghee, roasted gram flour, and cardamom. A classic Indian sweet.",
      ingredients: "Gram Flour (Besan), Pure Ghee, Sugar, Cardamom, Dry Fruits",
      benefits: "Rich in protein, good for digestion when made with pure ghee.",
      price: 450.00,
      imageUrl: "/images/besan-laddu.jpg",
      category: "Laddus",
      stock: 50
    },
    {
      name: "Gond Laddu",
      description: "Nutritious energy balls made with edible gum (Gond), wheat flour, ghee, and nuts. Perfect for winter and post-pregnancy.",
      ingredients: "Edible Gum (Gond), Wheat Flour, Ghee, Almonds, Cashews, Jaggery",
      benefits: "Strengthens bones, boosts immunity, excellent for new mothers.",
      price: 600.00,
      imageUrl: "/images/gond-laddu.jpg",
      category: "Laddus",
      stock: 30
    },
    {
      name: "Sethura (Panjiri)",
      description: "A traditional North Indian nutritional supplement made from whole wheat flour fried in sugar and ghee, heavily laced with dried fruits and herbal gums.",
      ingredients: "Whole Wheat Flour, Ghee, Sugar, Makhana, Gond, Dry Fruits",
      benefits: "Highly nutritious, provides warmth and energy.",
      price: 550.00,
      imageUrl: "/images/sethura.jpg",
      category: "Sethura",
      stock: 40
    },
    {
      name: "Kaju Katli",
      description: "Premium cashew fudge with silver leaf. The king of Indian sweets, made with minimal ingredients for maximum purity.",
      ingredients: "Cashew Nuts, Sugar, Ghee, Silver Leaf",
      benefits: "Good source of healthy fats and minerals.",
      price: 900.00,
      imageUrl: "/images/kaju-katli.jpg",
      category: "Festival Specials",
      stock: 25
    },
    {
      name: "Mysore Pak",
      description: "Rich, melt-in-the-mouth sweet made of generous amounts of ghee, sugar, and gram flour.",
      ingredients: "Gram Flour, Ghee, Sugar",
      benefits: "Instant energy booster.",
      price: 500.00,
      imageUrl: "/images/mysore-pak.jpg",
      category: "Festival Specials",
      stock: 35
    }
  ];

  for (const product of products) {
    await prisma.product.create({
      data: product
    });
  }

  console.log('Seed data inserted successfully');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
