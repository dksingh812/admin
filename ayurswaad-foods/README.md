# Ayurswaad Foods - The Taste of Life

Traditional Ayurvedic-inspired sweet brand focused on purity and legacy taste.

## Features

- **Home Page**: Hero section, Brand Story, Featured Products.
- **Shop**: Product listing with filters (mock).
- **Product Details**: Detailed view with Ingredients, Benefits, and Price.
- **Cart**: Client-side cart management (localStorage + Context API).
- **Checkout**: Simulated payment process and order creation.
- **Admin Dashboard**: View orders and manage inventory (mock auth).
- **Authentication**: Login/Register UI (mock).

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (Brand colors: Saffron, Cream, Deep Brown)
- **Database**: Prisma ORM with SQLite (Local) / PostgreSQL (Supabase ready)
- **Icons**: Lucide React

## Getting Started (Windows)

1.  **Run Automatic Setup**:
    Double-click `setup.bat`. This will install everything and setup the database.

2.  **Start Development Server**:
    In the terminal (or Command Prompt), run:
    ```bash
    npm run dev
    ```

3.  **Open Browser**:
    Navigate to [http://localhost:3000](http://localhost:3000).

## Manual Setup (Mac/Linux)

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Database Setup**:
    ```bash
    # Create .env file with DATABASE_URL="file:./dev.db"
    npx prisma db push
    node prisma/seed.js
    ```

3.  **Run Development Server**:
    ```bash
    npm run dev
    ```

## Project Structure

- `app/`: Next.js App Router pages and layouts.
- `components/`: Reusable UI components (Button, Header, ProductCard).
- `context/`: React Context (Cart state).
- `lib/`: Utility functions (Prisma client, Server Actions).
- `prisma/`: Database schema and seed script.
- `public/`: Static assets (images).

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on deploying to Vercel and connecting to Supabase.

## License

Private License.
